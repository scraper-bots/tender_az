"""
Job Discovery Agent - Phase 3
Adaptive scraping of jobs.glorri.az
"""

import asyncio
import uuid
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import aiohttp
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from src.agents.base_agent import BaseAgent
from src.models.schemas import JobPosting, JobStatus
from src.config.settings import settings

class JobDiscoveryAgent(BaseAgent):
    def __init__(self):
        super().__init__("job_discovery")
        self.base_url = "https://jobs.glorri.az"
        self.session = None
        self.driver = None
        self.discovered_jobs = set()  # Track discovered job URLs
    
    async def process(self, search_params: Optional[Dict[str, Any]] = None) -> List[JobPosting]:
        """Main processing function for job discovery"""
        try:
            self.log_info("Starting job discovery process")
            
            # Initialize scraping tools
            await self._init_session()
            
            # Scrape jobs
            jobs = await self._scrape_jobs(search_params or {})
            
            self.log_info(f"Discovered {len(jobs)} job postings")
            return jobs
            
        except Exception as e:
            self.log_error(f"Error in job discovery: {e}")
            return []
        finally:
            await self._cleanup()
    
    async def _init_session(self):
        """Initialize HTTP session and browser if needed"""
        # Initialize aiohttp session
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        
        # Initialize Selenium WebDriver for JavaScript-heavy pages
        if settings.selenium_headless:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
                self.driver.implicitly_wait(10)
            except Exception as e:
                self.log_warning(f"Could not initialize Chrome driver: {e}")
                self.driver = None
    
    async def _scrape_jobs(self, search_params: Dict[str, Any]) -> List[JobPosting]:
        """Scrape jobs from jobs.glorri.az"""
        jobs = []
        
        try:
            # First try with aiohttp for speed
            jobs_from_http = await self._scrape_with_http(search_params)
            jobs.extend(jobs_from_http)
            
            # If driver is available and we need more comprehensive scraping
            if self.driver and len(jobs) < 10:
                jobs_from_selenium = await self._scrape_with_selenium(search_params)
                jobs.extend(jobs_from_selenium)
            
            # Remove duplicates based on URL
            unique_jobs = {}
            for job in jobs:
                if job.url not in unique_jobs:
                    unique_jobs[job.url] = job
            
            return list(unique_jobs.values())
            
        except Exception as e:
            self.log_error(f"Error scraping jobs: {e}")
            return jobs
    
    async def _scrape_with_http(self, search_params: Dict[str, Any]) -> List[JobPosting]:
        """Fast scraping using aiohttp"""
        jobs = []
        
        try:
            # Build search URL
            search_url = self._build_search_url(search_params)
            
            async with self.session.get(search_url) as response:
                if response.status == 200:
                    html = await response.text()
                    jobs = await self._parse_job_listings(html)
                else:
                    self.log_warning(f"HTTP request failed with status {response.status}")
            
        except Exception as e:
            self.log_error(f"Error in HTTP scraping: {e}")
        
        return jobs
    
    async def _scrape_with_selenium(self, search_params: Dict[str, Any]) -> List[JobPosting]:
        """Comprehensive scraping using Selenium for JavaScript content"""
        jobs = []
        
        if not self.driver:
            return jobs
        
        try:
            # Build search URL
            search_url = self._build_search_url(search_params)
            
            self.driver.get(search_url)
            
            # Wait for job listings to load
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "job-listing"))
                )
            except TimeoutException:
                # Try alternative selectors
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='job']"))
                    )
                except TimeoutException:
                    self.log_warning("No job listings found on page")
                    return jobs
            
            # Scroll to load more jobs if needed
            await self._scroll_and_load_more()
            
            # Parse jobs from the page
            page_source = self.driver.page_source
            jobs = await self._parse_job_listings(page_source)
            
        except Exception as e:
            self.log_error(f"Error in Selenium scraping: {e}")
        
        return jobs
    
    def _build_search_url(self, search_params: Dict[str, Any]) -> str:
        """Build search URL with parameters"""
        base_url = self.base_url
        
        # Add search parameters
        params = []
        if search_params.get('keyword'):
            params.append(f"q={search_params['keyword']}")
        if search_params.get('location'):
            params.append(f"location={search_params['location']}")
        if search_params.get('category'):
            params.append(f"category={search_params['category']}")
        
        if params:
            base_url += "?" + "&".join(params)
        
        return base_url
    
    async def _parse_job_listings(self, html: str) -> List[JobPosting]:
        """Parse job listings from HTML"""
        jobs = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Try multiple selectors for job listings
            job_selectors = [
                '.job-listing',
                '.job-item',
                '.vacancy',
                '[class*="job"]',
                '.card',
                '.listing-item'
            ]
            
            job_elements = []
            for selector in job_selectors:
                elements = soup.select(selector)
                if elements:
                    job_elements = elements
                    self.log_info(f"Found {len(elements)} jobs using selector: {selector}")
                    break
            
            if not job_elements:
                self.log_warning("No job elements found with any selector")
                return jobs
            
            for element in job_elements:
                try:
                    job = await self._parse_single_job(element)
                    if job and job.url not in self.discovered_jobs:
                        jobs.append(job)
                        self.discovered_jobs.add(job.url)
                except Exception as e:
                    self.log_warning(f"Error parsing single job: {e}")
                    continue
            
        except Exception as e:
            self.log_error(f"Error parsing job listings: {e}")
        
        return jobs
    
    async def _parse_single_job(self, element) -> Optional[JobPosting]:
        """Parse a single job posting element"""
        try:
            # Extract job title
            title_selectors = ['h2', 'h3', '.title', '.job-title', '[class*="title"]']
            title = ""
            for selector in title_selectors:
                title_elem = element.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    break
            
            if not title:
                return None
            
            # Extract company
            company_selectors = ['.company', '.employer', '[class*="company"]', '[class*="employer"]']
            company = "Unknown"
            for selector in company_selectors:
                company_elem = element.select_one(selector)
                if company_elem:
                    company = company_elem.get_text(strip=True)
                    break
            
            # Extract location
            location_selectors = ['.location', '.city', '[class*="location"]']
            location = ""
            for selector in location_selectors:
                location_elem = element.select_one(selector)
                if location_elem:
                    location = location_elem.get_text(strip=True)
                    break
            
            # Extract job URL
            link_elem = element.select_one('a')
            job_url = ""
            if link_elem and link_elem.get('href'):
                href = link_elem.get('href')
                if href.startswith('http'):
                    job_url = href
                else:
                    job_url = f"{self.base_url.rstrip('/')}/{href.lstrip('/')}"
            
            # Extract description (limited)
            description_selectors = ['.description', '.summary', '.excerpt']
            description = ""
            for selector in description_selectors:
                desc_elem = element.select_one(selector)
                if desc_elem:
                    description = desc_elem.get_text(strip=True)[:500]
                    break
            
            # Extract salary if available
            salary_selectors = ['.salary', '.wage', '[class*="salary"]', '[class*="wage"]']
            salary = None
            for selector in salary_selectors:
                salary_elem = element.select_one(selector)
                if salary_elem:
                    salary = salary_elem.get_text(strip=True)
                    break
            
            # Create job posting
            job = JobPosting(
                id=str(uuid.uuid4()),
                title=title,
                company=company,
                location=location or "Remote",
                description=description or title,
                requirements=[],  # Will be filled by detailed scraping if needed
                salary_range=salary,
                url=job_url or f"{self.base_url}#{uuid.uuid4()}",
                discovered_at=datetime.now(),
                status=JobStatus.DISCOVERED
            )
            
            return job
            
        except Exception as e:
            self.log_error(f"Error parsing single job element: {e}")
            return None
    
    async def _scroll_and_load_more(self):
        """Scroll page to load more jobs if pagination is dynamic"""
        if not self.driver:
            return
        
        try:
            # Scroll to bottom to trigger lazy loading
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            await asyncio.sleep(2)
            
            # Look for "Load More" or "Next" buttons
            load_more_selectors = [
                '.load-more',
                '.next-page',
                '[class*="load"]',
                '[class*="more"]',
                'button[class*="next"]'
            ]
            
            for selector in load_more_selectors:
                try:
                    button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if button.is_displayed() and button.is_enabled():
                        button.click()
                        await asyncio.sleep(3)
                        break
                except NoSuchElementException:
                    continue
            
        except Exception as e:
            self.log_warning(f"Error in scroll and load more: {e}")
    
    async def get_job_details(self, job_url: str) -> Dict[str, Any]:
        """Get detailed information for a specific job"""
        try:
            if not self.session:
                await self._init_session()
            
            async with self.session.get(job_url) as response:
                if response.status == 200:
                    html = await response.text()
                    return await self._parse_job_details(html)
                else:
                    self.log_warning(f"Failed to fetch job details from {job_url}")
                    return {}
        
        except Exception as e:
            self.log_error(f"Error getting job details: {e}")
            return {}
    
    async def _parse_job_details(self, html: str) -> Dict[str, Any]:
        """Parse detailed job information from job detail page"""
        details = {
            'description': '',
            'requirements': [],
            'benefits': [],
            'employment_type': '',
            'experience_level': ''
        }
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract full description
            desc_selectors = ['.job-description', '.description', '.content', '.details']
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    details['description'] = desc_elem.get_text(strip=True)
                    break
            
            # Extract requirements from description
            description_text = details['description'].lower()
            common_requirements = [
                'python', 'javascript', 'react', 'node.js', 'sql', 'aws',
                'docker', 'kubernetes', 'git', 'agile', 'scrum', 'rest api',
                'html', 'css', 'postgresql', 'mongodb', 'redis', 'linux'
            ]
            
            found_requirements = []
            for req in common_requirements:
                if req in description_text:
                    found_requirements.append(req.title())
            
            details['requirements'] = found_requirements
            
        except Exception as e:
            self.log_error(f"Error parsing job details: {e}")
        
        return details
    
    async def _cleanup(self):
        """Clean up resources"""
        try:
            if self.session:
                await self.session.close()
            
            if self.driver:
                self.driver.quit()
                
        except Exception as e:
            self.log_error(f"Error during cleanup: {e}")
    
    async def health_check(self) -> bool:
        """Check if the agent can access the job site"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        self.log_info("Job discovery agent health check passed")
                        return True
                    else:
                        self.log_error(f"Job site returned status {response.status}")
                        return False
        except Exception as e:
            self.log_error(f"Job discovery agent health check failed: {e}")
            return False