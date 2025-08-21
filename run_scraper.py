#!/usr/bin/env python3

import sys
import argparse
from tender_scraper import TenderAzScraper
import json

def main():
    parser = argparse.ArgumentParser(description='Tender.az Company Scraper')
    parser.add_argument('--mode', choices=['test', 'pages', 'full', 'single'], 
                       default='test', help='Scraping mode')
    parser.add_argument('--start-page', type=int, default=1, help='Starting page number')
    parser.add_argument('--end-page', type=int, default=157, help='Ending page number (max 157)')
    parser.add_argument('--profile', type=str, help='Specific profile URL to scrape')
    parser.add_argument('--output', type=str, default='companies', help='Output filename prefix')
    
    args = parser.parse_args()
    
    scraper = TenderAzScraper()
    
    try:
        if args.mode == 'test':
            print("Running test mode - scraping first 3 pages...")
            scraper.run_test_scrape(num_pages=3)
            scraper.save_to_csv(f'{args.output}_test.csv')
            scraper.save_to_json(f'{args.output}_test.json')
            print(f"Test completed! Found {len(scraper.companies_data)} companies")
            
        elif args.mode == 'pages':
            print(f"Scraping pages {args.start_page} to {args.end_page}...")
            scraper.login()
            scraper.scrape_pages_range(args.start_page, args.end_page)
            scraper.save_to_csv(f'{args.output}_pages_{args.start_page}_{args.end_page}.csv')
            scraper.save_to_json(f'{args.output}_pages_{args.start_page}_{args.end_page}.json')
            print(f"Pages scraping completed! Found {len(scraper.companies_data)} companies")
            
        elif args.mode == 'single':
            if not args.profile:
                print("Please provide --profile URL for single mode")
                return
            print(f"Scraping single profile: {args.profile}")
            scraper.login()
            company_data = scraper.scrape_company_from_profile_url(args.profile)
            if company_data:
                print("Company data:")
                print(json.dumps(company_data, ensure_ascii=False, indent=2))
                scraper.companies_data = [company_data]
                scraper.save_to_csv(f'{args.output}_single.csv')
                scraper.save_to_json(f'{args.output}_single.json')
            else:
                print("Failed to scrape profile")
                
        elif args.mode == 'full':
            print("Running full scrape...")
            print(f"This will scrape all {args.end_page - args.start_page + 1} pages (~1879 companies)")
            print("This may take several hours! Periodic saves every 10 pages.")
            confirm = input("Continue? (y/N): ")
            if confirm.lower() == 'y':
                scraper.run_full_scrape(args.start_page, args.end_page)
            else:
                print("Full scrape cancelled")
        
        print("\nScraping completed successfully!")
        
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()