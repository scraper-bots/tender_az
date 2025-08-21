# Tender.az Company Scraper

A Python scraper for extracting company information from Tender.az, including contact details, ratings, and other business data.

## Features

- **Login Authentication**: Automated login using credentials from .env file
- **Company Data Extraction**: Extracts comprehensive company information including:
  - Company name and profile URL
  - Phone numbers (multiple formats supported)
  - WhatsApp numbers
  - Email addresses
  - Ratings and reviews
  - Experience information
  - Specialties and categories
  - Avatar/logo URLs
  - Activity status

- **Multiple Scraping Modes**:
  - Test mode (quick test with limited data)
  - Category mode (scrape specific business category)
  - Single profile mode (scrape individual company)
  - Full scrape mode (complete database scraping)

- **Data Export**: Saves data in both CSV and JSON formats

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your credentials in `.env` file:
```
Username=your_email@example.com
Password=your_password
```

## Usage

### Basic Usage

```bash
# Test mode - scrapes first category with 2 pages
python run_scraper.py --mode test

# Scrape specific category
python run_scraper.py --mode category --category "https://tender.az/users/tikinti-ve-temir" --pages 5

# Scrape single company profile
python run_scraper.py --mode single --profile "https://tender.az/user/yagmur2/portfolio/"

# Full scrape (WARNING: This may take hours!)
python run_scraper.py --mode full --pages 10
```

### Advanced Options

```bash
# Custom output filename
python run_scraper.py --mode test --output my_companies

# Limit pages per category
python run_scraper.py --mode category --category "URL" --pages 3
```

## Output Files

The scraper generates two types of output files:

- **CSV Format**: `companies.csv` - Spreadsheet-friendly format
- **JSON Format**: `companies.json` - Structured data format

### Data Fields

Each company record includes:
- `name`: Company/professional name
- `profile_url`: Direct link to profile
- `phones`: Phone numbers (semicolon-separated)
- `whatsapp`: WhatsApp numbers (semicolon-separated)
- `email`: Email address
- `rating`: Company rating
- `reviews_positive/neutral/negative`: Review counts
- `experience`: Years of experience
- `site_experience`: Time on Tender.az
- `last_active`: Last activity timestamp
- `specialties`: Services offered (semicolon-separated)
- `status`: Current status
- `avatar_url`: Profile image URL

## Rate Limiting

The scraper includes built-in delays to respect the website:
- 1 second between individual profiles
- 2 seconds between pages
- 5 seconds between categories

## Logging

All activities are logged to `tender_scraper.log` and console output.

## Modes Explained

### Test Mode
Perfect for testing the scraper setup. Scrapes only the first category with 2 pages.

### Category Mode
Scrape all companies from a specific business category. Get category URLs from the main users page.

### Single Profile Mode
Extract data from a single company profile. Useful for testing or targeted extraction.

### Full Scrape Mode
Scrapes all categories and companies. **Warning**: This can take several hours and generate thousands of records.

## Error Handling

The scraper includes robust error handling:
- Automatic login retry
- Graceful handling of missing data fields
- Network timeout management
- Periodic data saving during long scrapes

## Legal Considerations

- Respect robots.txt and website terms of service
- Use reasonable delays between requests
- Don't overload the server
- Use scraped data responsibly and in compliance with privacy laws