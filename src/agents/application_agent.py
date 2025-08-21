"""
Application Agent - Phase 5
Intelligent form submission and application management
"""

import asyncio
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
import aiohttp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from src.agents.base_agent import BaseAgent
from src.models.schemas import Application, ApplicationStatus, JobPosting, OptimizedResume
from src.config.settings import settings

class ApplicationAgent(BaseAgent):
    def __init__(self):
        super().__init__("application_agent")
        self.driver = None
        self.session = None
        self.application_queue = []
        
    async def process(self, optimized_resume: OptimizedResume, job_posting: JobPosting, cover_letter: Optional[str] = None) -> Application:
        """Main processing function for job applications"""
        try:
            self.log_info(f"Starting application for {job_posting.title} at {job_posting.company}")
            
            # Initialize browser and session
            await self._init_browser()
            
            # Create application record
            application = Application(
                id=str(uuid.uuid4()),
                job_posting_id=job_posting.id,
                resume_id=optimized_resume.original_resume_id,
                cover_letter=cover_letter,
                status=ApplicationStatus.IN_PROGRESS,
                submitted_at=None,
                notes=""
            )
            
            # Attempt to submit application
            success, notes = await self._submit_application(
                job_posting, optimized_resume, cover_letter
            )
            
            # Update application status
            if success:
                application.status = ApplicationStatus.COMPLETED
                application.submitted_at = datetime.now()
                application.notes = f"Successfully submitted. {notes}"
                self.log_info(f"Application submitted successfully for {job_posting.title}")
            else:
                application.status = ApplicationStatus.FAILED
                application.notes = f"Failed to submit. {notes}"
                self.log_error(f"Application failed for {job_posting.title}: {notes}")
            
            return application
            
        except Exception as e:
            self.log_error(f"Error processing application: {e}")
            
            # Return failed application
            return Application(
                id=str(uuid.uuid4()),
                job_posting_id=job_posting.id,
                resume_id=optimized_resume.original_resume_id,
                cover_letter=cover_letter,
                status=ApplicationStatus.FAILED,
                submitted_at=None,
                notes=f"Error during application: {str(e)}"
            )
        finally:
            await self._cleanup()
    
    async def _init_browser(self):
        """Initialize browser and session for applications"""
        try:
            # Setup Chrome options
            chrome_options = Options()
            if settings.selenium_headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Initialize WebDriver
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.implicitly_wait(10)
            
            # Initialize HTTP session
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            
        except Exception as e:
            self.log_error(f"Error initializing browser: {e}")
            raise
    
    async def _submit_application(
        self, 
        job_posting: JobPosting, 
        optimized_resume: OptimizedResume, 
        cover_letter: Optional[str]
    ) -> tuple[bool, str]:
        """Submit application to the job posting"""
        try:
            # Navigate to job posting
            self.driver.get(job_posting.url)
            await asyncio.sleep(3)
            
            # Look for application button/form
            apply_success = await self._find_and_click_apply_button()
            if not apply_success:
                return False, "Could not find apply button or form"
            
            # Fill out application form
            form_success, form_notes = await self._fill_application_form(
                optimized_resume, cover_letter
            )
            
            if not form_success:
                return False, f"Form filling failed: {form_notes}"
            
            # Submit the form (with confirmation)
            submit_success, submit_notes = await self._submit_form_with_confirmation()
            
            return submit_success, submit_notes
            
        except Exception as e:
            self.log_error(f"Error in application submission: {e}")
            return False, f"Submission error: {str(e)}"
    
    async def _find_and_click_apply_button(self) -> bool:
        """Find and click the apply button or navigate to application form"""
        apply_selectors = [
            'button[class*="apply"]',
            'a[class*="apply"]',
            '.apply-button',
            '.apply-btn',
            '[href*="apply"]',
            'button:contains("Apply")',
            'a:contains("Apply")',
            '.btn-primary',
            'button[type="submit"]'
        ]
        
        for selector in apply_selectors:
            try:
                # Try to find the element
                if selector.startswith('button:contains') or selector.startswith('a:contains'):
                    # Handle text-based selectors
                    elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), 'Apply')]")
                else:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        # Check if it's likely an apply button
                        text = element.get_attribute('textContent') or element.get_attribute('value') or ''
                        if any(word in text.lower() for word in ['apply', 'submit', 'send']):
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                            await asyncio.sleep(1)
                            element.click()
                            await asyncio.sleep(3)
                            return True
            
            except Exception as e:
                self.log_warning(f"Error with selector {selector}: {e}")
                continue
        
        return False
    
    async def _fill_application_form(
        self, 
        optimized_resume: OptimizedResume, 
        cover_letter: Optional[str]
    ) -> tuple[bool, str]:
        """Fill out the application form with resume data"""
        try:
            notes = []
            
            # Wait for form to load
            await asyncio.sleep(3)
            
            # Extract candidate info from optimized resume
            candidate_info = await self._extract_candidate_info(optimized_resume.optimized_content)
            
            # Fill common form fields
            field_mappings = {
                'name': candidate_info.get('name', ''),
                'first_name': candidate_info.get('first_name', ''),
                'last_name': candidate_info.get('last_name', ''),
                'email': candidate_info.get('email', ''),
                'phone': candidate_info.get('phone', ''),
                'address': candidate_info.get('address', ''),
                'city': candidate_info.get('city', ''),
                'country': candidate_info.get('country', ''),
                'linkedin': candidate_info.get('linkedin', ''),
                'website': candidate_info.get('website', ''),
            }
            
            # Fill text inputs
            for field_name, value in field_mappings.items():
                if value:
                    success = await self._fill_form_field(field_name, value)
                    if success:
                        notes.append(f"Filled {field_name}")
            
            # Handle file uploads (resume)
            resume_uploaded = await self._handle_file_upload('resume', optimized_resume)
            if resume_uploaded:
                notes.append("Resume uploaded")
            
            # Handle cover letter
            if cover_letter:
                cover_letter_filled = await self._fill_cover_letter(cover_letter)
                if cover_letter_filled:
                    notes.append("Cover letter filled")
            
            # Handle dropdowns and selections
            await self._handle_form_selections(candidate_info)
            notes.append("Form selections handled")
            
            return True, "; ".join(notes)
            
        except Exception as e:
            self.log_error(f"Error filling application form: {e}")
            return False, f"Form filling error: {str(e)}"
    
    async def _extract_candidate_info(self, resume_content: str) -> Dict[str, str]:
        """Extract candidate information from resume content"""
        import re
        
        info = {}
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, resume_content)
        if email_match:
            info['email'] = email_match.group()
        
        # Extract phone
        phone_pattern = r'[\+]?[1-9]?[0-9]{3}[-.\s]?[0-9]{3}[-.\s]?[0-9]{4,6}'
        phone_match = re.search(phone_pattern, resume_content)
        if phone_match:
            info['phone'] = phone_match.group()
        
        # Extract name (assume first line or first few words)
        lines = resume_content.strip().split('\n')
        if lines:
            first_line = lines[0].strip()
            if len(first_line.split()) <= 4 and not any(char.isdigit() for char in first_line):
                info['name'] = first_line
                parts = first_line.split()
                if len(parts) >= 2:
                    info['first_name'] = parts[0]
                    info['last_name'] = parts[-1]
        
        # Extract LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin_match = re.search(linkedin_pattern, resume_content, re.IGNORECASE)
        if linkedin_match:
            info['linkedin'] = f"https://{linkedin_match.group()}"
        
        return info
    
    async def _fill_form_field(self, field_name: str, value: str) -> bool:
        """Fill a specific form field by name or id"""
        selectors = [
            f'input[name*="{field_name}"]',
            f'input[id*="{field_name}"]',
            f'input[placeholder*="{field_name}"]',
            f'textarea[name*="{field_name}"]',
            f'textarea[id*="{field_name}"]',
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        element.clear()
                        element.send_keys(value)
                        await asyncio.sleep(0.5)
                        return True
            except Exception:
                continue
        
        return False
    
    async def _handle_file_upload(self, file_type: str, optimized_resume: OptimizedResume) -> bool:
        """Handle file upload for resume/CV"""
        try:
            # Create a temporary file with the optimized resume content
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                temp_file.write(optimized_resume.optimized_content)
                temp_file_path = temp_file.name
            
            # Find file upload input
            upload_selectors = [
                f'input[type="file"][name*="{file_type}"]',
                f'input[type="file"][id*="{file_type}"]',
                'input[type="file"]'
            ]
            
            for selector in upload_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            element.send_keys(temp_file_path)
                            await asyncio.sleep(2)
                            
                            # Clean up temp file
                            os.unlink(temp_file_path)
                            return True
                except Exception:
                    continue
            
            # Clean up temp file if upload failed
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            
            return False
            
        except Exception as e:
            self.log_error(f"Error handling file upload: {e}")
            return False
    
    async def _fill_cover_letter(self, cover_letter: str) -> bool:
        """Fill cover letter field"""
        cover_letter_selectors = [
            'textarea[name*="cover"]',
            'textarea[id*="cover"]',
            'textarea[placeholder*="cover"]',
            'textarea[name*="letter"]',
            'textarea[id*="letter"]',
            '.cover-letter textarea',
            'textarea[name*="message"]',
            'textarea[id*="message"]'
        ]
        
        for selector in cover_letter_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        element.clear()
                        element.send_keys(cover_letter)
                        await asyncio.sleep(1)
                        return True
            except Exception:
                continue
        
        return False
    
    async def _handle_form_selections(self, candidate_info: Dict[str, str]):
        """Handle dropdown selections and other form controls"""
        try:
            # Handle experience level dropdowns
            experience_selectors = [
                'select[name*="experience"]',
                'select[id*="experience"]',
                'select[name*="level"]'
            ]
            
            for selector in experience_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            select = Select(element)
                            # Select middle option as default
                            options = select.options
                            if len(options) > 2:
                                select.select_by_index(len(options) // 2)
                except Exception:
                    continue
            
            # Handle authorization questions (work authorization, visa status, etc.)
            await self._handle_authorization_questions()
            
        except Exception as e:
            self.log_warning(f"Error handling form selections: {e}")
    
    async def _handle_authorization_questions(self):
        """Handle common authorization and eligibility questions"""
        # Common yes/no questions that should be answered "yes" for most cases
        positive_keywords = [
            'authorized', 'eligible', 'willing', 'available', 'relocate'
        ]
        
        # Find radio buttons and checkboxes
        inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="radio"], input[type="checkbox"]')
        
        for input_elem in inputs:
            try:
                # Get associated label or nearby text
                label_text = ""
                
                # Try to find associated label
                label_id = input_elem.get_attribute('id')
                if label_id:
                    label = self.driver.find_element(By.CSS_SELECTOR, f'label[for="{label_id}"]')
                    label_text = label.text.lower()
                
                # Check if this looks like an authorization question
                if any(keyword in label_text for keyword in positive_keywords):
                    # Select "yes" or positive option
                    value = input_elem.get_attribute('value')
                    if value and value.lower() in ['yes', 'true', '1']:
                        if not input_elem.is_selected():
                            input_elem.click()
                            await asyncio.sleep(0.5)
                
            except Exception:
                continue
    
    async def _submit_form_with_confirmation(self) -> tuple[bool, str]:
        """Submit the form and confirm submission"""
        try:
            # Look for submit button
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button[class*="submit"]',
                '.submit-btn',
                '.btn-submit',
                'button:contains("Submit")',
                'button:contains("Send")',
                'button:contains("Apply")'
            ]
            
            submitted = False
            for selector in submit_selectors:
                try:
                    if selector.startswith('button:contains'):
                        elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), 'Submit') or contains(text(), 'Send') or contains(text(), 'Apply')]")
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            # Scroll into view and click
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                            await asyncio.sleep(1)
                            element.click()
                            await asyncio.sleep(5)
                            submitted = True
                            break
                    
                    if submitted:
                        break
                        
                except Exception:
                    continue
            
            if not submitted:
                return False, "Could not find or click submit button"
            
            # Wait for confirmation or success message
            confirmation_found = await self._wait_for_confirmation()
            
            if confirmation_found:
                return True, "Application submitted successfully with confirmation"
            else:
                return True, "Application likely submitted (no explicit confirmation found)"
            
        except Exception as e:
            self.log_error(f"Error submitting form: {e}")
            return False, f"Submission error: {str(e)}"
    
    async def _wait_for_confirmation(self) -> bool:
        """Wait for and detect submission confirmation"""
        try:
            # Wait a bit for page to process
            await asyncio.sleep(3)
            
            # Look for success indicators
            success_indicators = [
                '.success',
                '.confirmation',
                '.thank-you',
                '[class*="success"]',
                '[class*="confirmation"]',
                '[class*="submitted"]'
            ]
            
            for selector in success_indicators:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            text = element.text.lower()
                            if any(word in text for word in ['success', 'submitted', 'thank', 'received', 'application']):
                                return True
                except Exception:
                    continue
            
            # Check page title and URL changes
            current_url = self.driver.current_url
            page_title = self.driver.title.lower()
            
            if any(word in current_url.lower() for word in ['success', 'confirmation', 'thank']) or \
               any(word in page_title for word in ['success', 'submitted', 'thank']):
                return True
            
            return False
            
        except Exception as e:
            self.log_warning(f"Error waiting for confirmation: {e}")
            return False
    
    async def batch_apply(self, applications: List[tuple[OptimizedResume, JobPosting, Optional[str]]]) -> List[Application]:
        """Apply to multiple jobs in batch with rate limiting"""
        results = []
        
        for i, (optimized_resume, job_posting, cover_letter) in enumerate(applications):
            try:
                self.log_info(f"Processing application {i+1}/{len(applications)}")
                
                # Check daily application limit
                if i >= settings.max_applications_per_day:
                    self.log_warning(f"Daily application limit reached ({settings.max_applications_per_day})")
                    break
                
                # Process application
                application = await self.process(optimized_resume, job_posting, cover_letter)
                results.append(application)
                
                # Rate limiting between applications
                if i < len(applications) - 1:  # Don't wait after last application
                    await asyncio.sleep(settings.request_delay * 10)  # Longer delay between applications
                
            except Exception as e:
                self.log_error(f"Error in batch application {i+1}: {e}")
                # Create failed application record
                failed_app = Application(
                    id=str(uuid.uuid4()),
                    job_posting_id=job_posting.id,
                    resume_id=optimized_resume.original_resume_id,
                    cover_letter=cover_letter,
                    status=ApplicationStatus.FAILED,
                    submitted_at=None,
                    notes=f"Batch processing error: {str(e)}"
                )
                results.append(failed_app)
        
        return results
    
    async def _cleanup(self):
        """Clean up resources"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
            
            if self.session:
                await self.session.close()
                self.session = None
                
        except Exception as e:
            self.log_error(f"Error during cleanup: {e}")
    
    async def health_check(self) -> bool:
        """Check if the agent can initialize browser"""
        try:
            await self._init_browser()
            await self._cleanup()
            self.log_info("Application agent health check passed")
            return True
        except Exception as e:
            self.log_error(f"Application agent health check failed: {e}")
            return False