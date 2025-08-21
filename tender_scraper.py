#!/usr/bin/env python3

import requests
import json
import csv
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tender_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TenderAzScraper:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://tender.az"
        self.login_url = "https://tender.az/user/login"
        self.users_url = "https://tender.az/users/"
        
        # Set user agent to avoid blocking
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7,az;q=0.6',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
        })
        
        # Get credentials from environment
        self.username = os.getenv('Username')
        self.password = os.getenv('Password')
        
        if not self.username or not self.password:
            raise ValueError("Username and Password must be set in .env file")
        
        self.companies_data = []
        
    def login(self):
        """Login to Tender.az"""
        logger.info("Attempting to login...")
        
        # First, get the login page to extract any necessary tokens
        login_page = self.session.get(self.login_url)
        if login_page.status_code != 200:
            logger.error(f"Failed to access login page: {login_page.status_code}")
            return False
            
        soup = BeautifulSoup(login_page.content, 'html.parser')
        
        # Look for CSRF token or similar
        csrf_token = None
        csrf_input = soup.find('input', {'name': '_token'}) or soup.find('input', {'name': 'csrf_token'})
        if csrf_input:
            csrf_token = csrf_input.get('value')
        
        # Prepare login data - correct field names from form analysis
        login_data = {
            'email': self.username,
            'pass': self.password,  # Field is 'pass' not 'password'
            'remember': 1,
            'back': self.base_url  # Add back field
        }
        
        if csrf_token:
            login_data['_token'] = csrf_token
            
        # Set headers for AJAX request
        login_headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Origin': self.base_url,
            'Referer': self.login_url
        }
        
        # Attempt login
        response = self.session.post(
            self.login_url,
            data=login_data,
            headers=login_headers
        )
        
        if response.status_code == 200:
            try:
                result = response.json()
                # Check if login was successful - Tender.az returns success: True and status: 2
                if result.get('data', {}).get('success') or result.get('success'):
                    logger.info("Login successful!")
                    return True
                else:
                    logger.error(f"Login failed: {result}")
                    return False
            except json.JSONDecodeError:
                # If not JSON, check if we're redirected or have success indicators
                if 'dashboard' in response.text or 'profile' in response.text:
                    logger.info("Login successful!")
                    return True
                else:
                    logger.error("Login failed - unexpected response")
                    return False
        else:
            logger.error(f"Login request failed with status: {response.status_code}")
            return False
    
    def scrape_page_companies(self, page_num):
        """Extract company profile URLs from a specific page"""
        page_url = f"https://tender.az/users/?page={page_num}"
        logger.info(f"Scraping companies from page {page_num}: {page_url}")
        
        response = self.session.get(page_url)
        if response.status_code != 200:
            logger.error(f"Failed to access page {page_num}: {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.content, 'html.parser')
        profile_urls = []
        
        # Find the company listings container
        listings_container = soup.find('div', class_='j-list')
        if not listings_container:
            logger.warning(f"No listings container found on page {page_num}")
            return []
            
        # Find all company profile links in the listings
        company_list = listings_container.find('ul', class_='o-freelancersList')
        if company_list:
            # Each company is in an <li class="media"> element
            company_items = company_list.find_all('li', class_='media')
            
            for item in company_items:
                # Look for the main profile link
                profile_link = item.find('a', class_='f-freelancer-avatar')
                if profile_link and profile_link.get('href'):
                    profile_url = urljoin(self.base_url, profile_link.get('href'))
                    # Ensure we get the main profile URL, not portfolio
                    if '/portfolio/' not in profile_url and profile_url not in profile_urls:
                        profile_urls.append(profile_url)
                
                # Also check for company name link as backup
                if not profile_link:
                    name_div = item.find('div', class_='f-freelancer-name')
                    if name_div:
                        name_link = name_div.find('a')
                        if name_link and name_link.get('href'):
                            profile_url = urljoin(self.base_url, name_link.get('href'))
                            if '/portfolio/' not in profile_url and profile_url not in profile_urls:
                                profile_urls.append(profile_url)
        
        logger.info(f"Found {len(profile_urls)} companies on page {page_num}")
        return profile_urls
    
    def scrape_company_from_profile_url(self, profile_url):
        """Scrape detailed company information from profile URL"""
        logger.info(f"Scraping company profile: {profile_url}")
        
        try:
            response = self.session.get(profile_url)
            if response.status_code != 200:
                logger.warning(f"Failed to access profile: {profile_url}")
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            company_data = {
                'profile_url': profile_url,
                'name': '',
                'phones': [],
                'whatsapp': [],
                'email': '',
                'rating': '',
                'reviews_positive': 0,
                'reviews_neutral': 0,
                'reviews_negative': 0,
                'experience': '',
                'site_experience': '',
                'last_active': '',
                'specialties': [],
                'status': '',
                'avatar_url': ''
            }
            
            # Extract company name
            name_elem = soup.find('h6')
            if name_elem:
                company_data['name'] = name_elem.text.strip()
            
            # Extract contact information - improved pattern for Azerbaijani phone numbers
            # Format: 050-222-92-52, 077-404-54-00, 012-465-94-27
            # Also handle: 0502889559 (10 digits), 9945023411 (10 digits)
            phone_patterns = [
                re.compile(r'(\d{3}[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2})'),  # 050-222-92-52 format
                re.compile(r'(\d{10})'),  # 0502889559 format (10 digits)
                re.compile(r'(\d{3}[-\s]?\d{2}[-\s]?\d{3}[-\s]?\d{2})'),  # Alternative format
            ]
            
            # Look for all contact information in the page
            all_text = soup.get_text()
            
            # Find the contact section specifically
            contact_section = soup.find('h6', string='Əlaqə')
            if contact_section:
                # Get the parent div and find the contact list
                contact_parent = contact_section.find_parent('div', class_='l-inside')
                if contact_parent:
                    contact_list = contact_parent.find('ul', class_='p-profile-info-list')
                    if contact_list:
                        for li in contact_list.find_all('li'):
                            li_html = str(li)
                            li_text = li.get_text().strip()
                            
                            # Look for phone icon and extract number
                            if 'fa-phone' in li_html:
                                for pattern in phone_patterns:
                                    phones = pattern.findall(li_text)
                                    for phone in phones:
                                        if phone not in company_data['phones']:
                                            company_data['phones'].append(phone)
                            
                            # Look for WhatsApp icon and extract number  
                            elif 'fa-whatsapp' in li_html:
                                for pattern in phone_patterns:
                                    whatsapp = pattern.findall(li_text)
                                    for wa in whatsapp:
                                        if wa not in company_data['whatsapp']:
                                            company_data['whatsapp'].append(wa)
                            
                            # Look for email
                            elif '@' in li_text:
                                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', li_text)
                                if email_match and not company_data['email']:
                                    company_data['email'] = email_match.group()
            
            # Fallback: search all li elements if contact section wasn't found
            if not company_data['phones'] and not company_data['whatsapp']:
                phone_lines = soup.find_all('li')
                for li in phone_lines:
                    li_html = str(li)
                    li_text = li.get_text().strip()
                    
                    # Look for phone icon and extract number
                    if 'fa-phone' in li_html:
                        for pattern in phone_patterns:
                            phones = pattern.findall(li_text)
                            for phone in phones:
                                if phone not in company_data['phones']:
                                    company_data['phones'].append(phone)
                    
                    # Look for WhatsApp icon and extract number  
                    elif 'fa-whatsapp' in li_html:
                        for pattern in phone_patterns:
                            whatsapp = pattern.findall(li_text)
                            for wa in whatsapp:
                                if wa not in company_data['whatsapp']:
                                    company_data['whatsapp'].append(wa)
                    
                    # Look for email
                    elif '@' in li_text:
                        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', li_text)
                        if email_match and not company_data['email']:
                            company_data['email'] = email_match.group()
            
            # Additional phone search but only in the contact section to avoid global numbers
            # Skip searching entire page content which may include site-wide contact info
            if contact_section:
                contact_parent = contact_section.find_parent('div', class_='l-inside')
                if contact_parent:
                    contact_text = contact_parent.get_text()
                    
                    for pattern in phone_patterns:
                        all_phones = pattern.findall(contact_text)
                        for phone in all_phones:
                            # Skip if it's just part of a longer number or not actually a phone
                            if len(phone.replace('-', '').replace(' ', '')) < 9:
                                continue
                                
                            cleaned_phone = phone.replace(' ', '-') if '-' not in phone else phone
                            
                            # Check if this appears near WhatsApp icon in the contact section
                            is_whatsapp = False
                            for li in contact_parent.find_all('li'):
                                if 'fa-whatsapp' in str(li) and phone in li.get_text():
                                    is_whatsapp = True
                                    break
                            
                            if is_whatsapp:
                                if cleaned_phone not in company_data['whatsapp']:
                                    company_data['whatsapp'].append(cleaned_phone)
                            else:
                                # Avoid adding duplicate numbers (compare digits only)
                                phone_digits = cleaned_phone.replace('-', '').replace(' ', '')
                                is_duplicate = any(
                                    p.replace('-', '').replace(' ', '') == phone_digits 
                                    for p in company_data['phones']
                                )
                                if not is_duplicate:
                                    company_data['phones'].append(cleaned_phone)
            
            # Extract rating and reviews
            rating_elem = soup.find('span', class_='text-success')
            if rating_elem:
                company_data['rating'] = rating_elem.text.strip()
            
            # Extract review counts
            reviews_elem = soup.find('span', id='j-user-opinions-cache')
            if reviews_elem:
                review_links = reviews_elem.find_all('a')
                for link in review_links:
                    if 'o-good' in link.get('class', []):
                        company_data['reviews_positive'] = re.findall(r'\d+', link.text)
                        company_data['reviews_positive'] = int(company_data['reviews_positive'][0]) if company_data['reviews_positive'] else 0
                    elif 'o-bad' in link.get('class', []):
                        company_data['reviews_negative'] = re.findall(r'\d+', link.text)
                        company_data['reviews_negative'] = int(company_data['reviews_negative'][0]) if company_data['reviews_negative'] else 0
                    else:
                        neutral_count = re.findall(r'\d+', link.text)
                        if neutral_count:
                            company_data['reviews_neutral'] = int(neutral_count[0])
            
            # Extract experience information
            exp_section = soup.find('div', class_='l-inside')
            if exp_section and 'Təcrübə' in exp_section.text:
                exp_list = exp_section.find('ul', class_='p-profile-info-list')
                if exp_list:
                    for li in exp_list.find_all('li'):
                        text = li.text.strip()
                        if 'Təcrübə:' in text:
                            company_data['experience'] = text.replace('Təcrübə:', '').strip()
                        elif 'Saytda:' in text:
                            company_data['site_experience'] = text.replace('Saytda:', '').strip()
                        elif 'Saytda olub:' in text:
                            company_data['last_active'] = text.replace('Saytda olub:', '').strip()
            
            # Extract specialties
            spec_links = soup.find_all('a', href=re.compile(r'/users/[^/]+/[^/]+/?'))
            for link in spec_links:
                if link.find('b'):  # Specialty links have bold text
                    specialty = link.find('b').text.strip()
                    if specialty and specialty not in company_data['specialties']:
                        company_data['specialties'].append(specialty)
            
            # Extract status
            status_elem = soup.find('span', class_='label')
            if status_elem:
                company_data['status'] = status_elem.text.strip()
            
            # Extract avatar URL
            avatar_elem = soup.find('img', src=re.compile(r'/files/images/avatars/'))
            if avatar_elem:
                company_data['avatar_url'] = urljoin(self.base_url, avatar_elem.get('src'))
            
            # Clean up phone numbers - prefer formatted versions
            cleaned_phones = []
            cleaned_whatsapp = []
            
            # For phones, prefer formatted versions (with dashes)
            for phone in company_data['phones']:
                # If this is a formatted number, add it
                if '-' in phone:
                    cleaned_phones.append(phone)
                # If unformatted, only add if no formatted version exists
                else:
                    digits_only = phone.replace('-', '').replace(' ', '')
                    has_formatted = any('-' in p and p.replace('-', '').replace(' ', '') == digits_only for p in company_data['phones'])
                    if not has_formatted:
                        cleaned_phones.append(phone)
            
            # Same for WhatsApp
            for wa in company_data['whatsapp']:
                if '-' in wa:
                    cleaned_whatsapp.append(wa)
                else:
                    digits_only = wa.replace('-', '').replace(' ', '')
                    has_formatted = any('-' in w and w.replace('-', '').replace(' ', '') == digits_only for w in company_data['whatsapp'])
                    if not has_formatted:
                        cleaned_whatsapp.append(wa)
            
            company_data['phones'] = cleaned_phones
            company_data['whatsapp'] = cleaned_whatsapp
            
            logger.info(f"Successfully scraped: {company_data['name']}")
            return company_data
            
        except Exception as e:
            logger.error(f"Error scraping profile {profile_url}: {str(e)}")
            return None
    
    def scrape_category(self, category_url, max_pages=None):
        """Scrape all companies from a specific category"""
        logger.info(f"Scraping category: {category_url}")
        
        page = 1
        companies_found = 0
        
        while True:
            if max_pages and page > max_pages:
                break
                
            # Build page URL
            if page == 1:
                page_url = category_url
            else:
                page_url = f"{category_url.rstrip('/')}/page/{page}"
            
            logger.info(f"Scraping page {page}: {page_url}")
            
            try:
                response = self.session.get(page_url)
                if response.status_code != 200:
                    logger.warning(f"Failed to access page {page}: {response.status_code}")
                    break
                    
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find profile links on this page
                profile_links = []
                processed_usernames = set()
                
                # Look for main user profile links only (not portfolio or opinion pages)
                for link in soup.find_all('a', href=re.compile(r'/user/[^/]+/?$')):
                    href = link.get('href', '')
                    
                    # Skip system pages and non-profile URLs
                    skip_urls = ['/login', '/register', '/opinions', '/portfolio', '?', 
                                '/messages', '/settings', '/logout', '/bill', '/dashboard', 
                                '/notifications', '/orders', '/shop']
                    if any(skip in href for skip in skip_urls):
                        continue
                    
                    # Extract username from URL
                    username_match = re.search(r'/user/([^/]+)/?$', href)
                    if username_match:
                        username = username_match.group(1)
                        
                        # Skip if we already processed this username
                        if username in processed_usernames:
                            continue
                            
                        profile_url = urljoin(self.base_url, href)
                        
                        # Make sure it's not already in our data
                        if not any(profile_url == p['profile_url'] for p in self.companies_data):
                            profile_links.append(profile_url)
                            processed_usernames.add(username)
                
                if not profile_links:
                    logger.info(f"No more companies found on page {page}")
                    break
                
                # Scrape each company profile
                for profile_url in profile_links:
                    company_data = self.scrape_company_from_profile_url(profile_url)
                    if company_data:
                        self.companies_data.append(company_data)
                        companies_found += 1
                    
                    # Add delay to avoid being blocked
                    time.sleep(1)
                
                logger.info(f"Page {page} completed. Found {len(profile_links)} companies.")
                page += 1
                
                # Add delay between pages
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error scraping page {page}: {str(e)}")
                break
        
        logger.info(f"Category scraping completed. Found {companies_found} companies.")
        return companies_found
    
    def save_to_csv(self, filename='tender_companies.csv'):
        """Save scraped data to CSV file"""
        if not self.companies_data:
            logger.warning("No data to save")
            return
            
        logger.info(f"Saving {len(self.companies_data)} companies to {filename}")
        
        fieldnames = [
            'name', 'profile_url', 'phones', 'whatsapp', 'email', 'rating',
            'reviews_positive', 'reviews_neutral', 'reviews_negative',
            'experience', 'site_experience', 'last_active', 'specialties',
            'status', 'avatar_url'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for company in self.companies_data:
                # Convert lists to strings for CSV
                row = company.copy()
                row['phones'] = '; '.join(row['phones']) if row['phones'] else ''
                row['whatsapp'] = '; '.join(row['whatsapp']) if row['whatsapp'] else ''
                row['specialties'] = '; '.join(row['specialties']) if row['specialties'] else ''
                
                writer.writerow(row)
        
        logger.info(f"Data saved to {filename}")
    
    def save_to_json(self, filename='tender_companies.json'):
        """Save scraped data to JSON file"""
        if not self.companies_data:
            logger.warning("No data to save")
            return
            
        logger.info(f"Saving {len(self.companies_data)} companies to {filename}")
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(self.companies_data, jsonfile, ensure_ascii=False, indent=2)
        
        logger.info(f"Data saved to {filename}")
    
    def run_full_scrape(self, max_pages_per_category=5):
        """Run full scraping process"""
        logger.info("Starting full scrape of Tender.az")
        
        # Login
        if not self.login():
            logger.error("Failed to login. Exiting.")
            return
        
        # Get all categories
        categories = self.get_categories()
        if not categories:
            logger.error("Failed to get categories. Exiting.")
            return
        
        # Scrape each category
        total_companies = 0
        for i, category in enumerate(categories, 1):
            logger.info(f"Processing category {i}/{len(categories)}: {category['name']}")
            
            count = self.scrape_category(category['url'], max_pages_per_category)
            total_companies += count
            
            # Save periodically
            if i % 5 == 0:
                self.save_to_csv(f'tender_companies_partial_{i}.csv')
                self.save_to_json(f'tender_companies_partial_{i}.json')
            
            # Add delay between categories
            time.sleep(5)
        
        # Final save
        self.save_to_csv()
        self.save_to_json()
        
        logger.info(f"Scraping completed! Total companies found: {total_companies}")

if __name__ == "__main__":
    scraper = TenderAzScraper()
    
    # You can run different modes:
    
    # 1. Full scrape (might take hours)
    # scraper.run_full_scrape(max_pages_per_category=10)
    
    # 2. Test with single category
    scraper.login()
    categories = scraper.get_categories()
    if categories:
        # Test with first category, only 2 pages
        scraper.scrape_category(categories[0]['url'], max_pages=2)
        scraper.save_to_csv('test_companies.csv')
        scraper.save_to_json('test_companies.json')
    
    # 3. Scrape specific URL
    # scraper.login()
    # company_data = scraper.scrape_company_from_profile_url('https://tender.az/user/yagmur2/portfolio/')
    # if company_data:
    #     print(json.dumps(company_data, ensure_ascii=False, indent=2))