#!/usr/bin/env python3

import sys
import argparse
from tender_scraper import TenderAzScraper
import json

def main():
    parser = argparse.ArgumentParser(description='Tender.az Company Scraper')
    parser.add_argument('--mode', choices=['test', 'category', 'full', 'single'], 
                       default='test', help='Scraping mode')
    parser.add_argument('--category', type=str, help='Specific category URL to scrape')
    parser.add_argument('--profile', type=str, help='Specific profile URL to scrape')
    parser.add_argument('--pages', type=int, default=5, help='Max pages per category')
    parser.add_argument('--output', type=str, default='companies', help='Output filename prefix')
    
    args = parser.parse_args()
    
    scraper = TenderAzScraper()
    
    try:
        if args.mode == 'test':
            print("Running test mode - scraping first category with 2 pages...")
            scraper.login()
            categories = scraper.get_categories()
            if categories:
                scraper.scrape_category(categories[0]['url'], max_pages=2)
                scraper.save_to_csv(f'{args.output}_test.csv')
                scraper.save_to_json(f'{args.output}_test.json')
                print(f"Test completed! Found {len(scraper.companies_data)} companies")
            
        elif args.mode == 'category':
            if not args.category:
                print("Please provide --category URL for category mode")
                return
            print(f"Scraping category: {args.category}")
            scraper.login()
            scraper.scrape_category(args.category, max_pages=args.pages)
            scraper.save_to_csv(f'{args.output}_category.csv')
            scraper.save_to_json(f'{args.output}_category.json')
            print(f"Category scraping completed! Found {len(scraper.companies_data)} companies")
            
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
            print("This may take several hours depending on the number of categories and pages")
            confirm = input("Continue? (y/N): ")
            if confirm.lower() == 'y':
                scraper.run_full_scrape(max_pages_per_category=args.pages)
            else:
                print("Full scrape cancelled")
        
        print("\nScraping completed successfully!")
        
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()