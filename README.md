# Tender.az Company Scraper

A Python scraper for extracting company information from Tender.az using efficient page-by-page scraping. Capable of extracting all **1,879 companies** across **157 pages** (~12 companies per page).

## Features

- **Login Authentication**: Automated login using credentials from .env file
- **Page-by-Page Scraping**: Efficient extraction from paginated company listings
- **Complete Phone Number Extraction**: Extracts phone numbers in all formats:
  - Formatted: `050-222-92-52`, `012-465-94-27`
  - Unformatted: `0502889559`, `9945023411`
  - International: `994 50-232-00`, `994 12 310 09`
- **Company Data Extraction**: Extracts comprehensive company information including:
  - Company name and profile URL
  - Phone numbers (multiple formats supported)
  - WhatsApp numbers (properly separated)
  - Email addresses and websites
  - Ratings and reviews
  - Experience information
  - Specialties and categories
  - Avatar/logo URLs
  - Activity status

- **Multiple Scraping Modes**:
  - Test mode (scrape first 3 pages ~36 companies)
  - Pages mode (scrape specific page range)
  - Single profile mode (scrape individual company)
  - Full scrape mode (all 157 pages ~1,879 companies)

- **Data Export**: Saves data in both CSV and JSON formats
- **Automatic Periodic Saves**: Saves progress every 10 pages during long scrapes

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
# Test mode - scrapes first 3 pages (~36 companies)
python run_scraper.py --mode test

# Scrape specific page range
python run_scraper.py --mode pages --start-page 1 --end-page 10

# Scrape single company profile
python run_scraper.py --mode single --profile "https://tender.az/user/yagmur2/"

# Full scrape - all 157 pages (~1,879 companies)
# WARNING: This may take 3-4 hours!
python run_scraper.py --mode full
```

### Advanced Options

```bash
# Custom output filename
python run_scraper.py --mode test --output my_companies

# Scrape specific page range
python run_scraper.py --mode pages --start-page 50 --end-page 100 --output batch2

# Scrape from middle of database
python run_scraper.py --mode pages --start-page 80 --end-page 120
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
Perfect for testing the scraper setup. Scrapes the first 3 pages (~36 companies) to verify everything works.

### Pages Mode
Scrape companies from a specific page range. Useful for:
- Processing data in batches
- Resuming interrupted scrapes
- Parallel processing (different page ranges)

### Single Profile Mode
Extract data from a single company profile. Useful for testing or targeted extraction.

### Full Scrape Mode
Scrapes all 157 pages (~1,879 companies). **Features:**
- **Automatic periodic saves** every 10 pages
- **Progress tracking** with detailed logging
- **Resume capability** by checking existing files
- **Estimated time**: 3-4 hours depending on connection speed

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