#!/usr/bin/env python3
"""
Command Line Interface for the AI Career Agent
Provides easy access to all agent functionalities
"""

import asyncio
import argparse
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from src.orchestrator import JobApplicationOrchestrator
from src.config.settings import settings
from loguru import logger

class CareerAgentCLI:
    def __init__(self):
        self.orchestrator = JobApplicationOrchestrator()
        
    async def process_resume(self, resume_path: str, interactive: bool = True):
        """Process a single resume"""
        try:
            print(f"🔄 Processing resume: {resume_path}")
            
            await self.orchestrator.start_agents()
            resume = await self.orchestrator.process_resume(resume_path)
            
            print(f"✅ Resume processed successfully!")
            print(f"   📄 ID: {resume.id}")
            print(f"   🛠️  Skills: {len(resume.skills)} found")
            print(f"   ⏱️  Experience: {resume.experience_years} years")
            
            if resume.skills:
                print(f"   🔧 Top skills: {', '.join(resume.skills[:5])}")
            
        except Exception as e:
            print(f"❌ Error processing resume: {e}")
            sys.exit(1)
    
    async def discover_jobs(self, search_params: Optional[Dict[str, Any]] = None):
        """Discover job opportunities"""
        try:
            print("🔍 Discovering job opportunities...")
            
            await self.orchestrator.start_agents()
            jobs = await self.orchestrator.discover_jobs(search_params)
            
            print(f"✅ Discovered {len(jobs)} job opportunities!")
            
            for i, job in enumerate(jobs[:5], 1):  # Show first 5
                print(f"\n   {i}. {job.title} at {job.company}")
                print(f"      📍 {job.location}")
                print(f"      🔗 {job.url}")
                if job.salary_range:
                    print(f"      💰 {job.salary_range}")
            
            if len(jobs) > 5:
                print(f"\n   ... and {len(jobs) - 5} more jobs")
            
        except Exception as e:
            print(f"❌ Error discovering jobs: {e}")
            sys.exit(1)
    
    async def run_full_workflow(self, resume_path: str, search_params: Optional[Dict[str, Any]] = None):
        """Run the complete job application workflow"""
        try:
            print("🚀 Starting full job application workflow...")
            print("="*50)
            
            await self.orchestrator.start_agents()
            results = await self.orchestrator.full_application_workflow(resume_path, search_params)
            
            # Display results
            print("\n📊 Workflow Results:")
            print("="*30)
            print(f"📄 Resume processed: {'✅' if results['resume_processed'] else '❌'}")
            print(f"🔍 Jobs discovered: {results['jobs_discovered']}")
            print(f"📤 Applications submitted: {results['applications_submitted']}")
            print(f"✅ Successful applications: {results['successful_applications']}")
            print(f"❌ Failed applications: {results['failed_applications']}")
            
            if results['applications']:
                print(f"\n📋 Application Details:")
                for i, app in enumerate(results['applications'], 1):
                    status_icon = "✅" if app['status'] == 'completed' else "❌"
                    print(f"   {i}. {status_icon} {app['job_title']} at {app['company']}")
                    print(f"      📊 Match score: {app['match_score']:.2f}")
                    if app['submitted_at']:
                        print(f"      ⏰ Submitted: {app['submitted_at']}")
            
        except Exception as e:
            print(f"❌ Error in full workflow: {e}")
            sys.exit(1)
    
    async def batch_process_resumes(self, resume_directory: str):
        """Process multiple resumes from a directory"""
        try:
            print(f"📁 Processing resumes from: {resume_directory}")
            
            await self.orchestrator.start_agents()
            resumes = await self.orchestrator.batch_process_resumes(resume_directory)
            
            print(f"✅ Processed {len(resumes)} resumes!")
            
            for resume in resumes:
                print(f"   📄 {resume.file_path} - {len(resume.skills)} skills, {resume.experience_years} years exp")
            
        except Exception as e:
            print(f"❌ Error in batch processing: {e}")
            sys.exit(1)
    
    async def generate_report(self):
        """Generate and display system performance report"""
        try:
            print("📈 Generating performance report...")
            
            await self.orchestrator.start_agents()
            report = await self.orchestrator.generate_performance_report()
            
            print("\n📊 System Performance Report")
            print("="*40)
            print(f"🔍 Total jobs discovered: {report['total_jobs_discovered']}")
            print(f"⏳ Pending applications: {report['pending_applications']}")
            
            print(f"\n🏥 Agent Health Status:")
            for agent_name, status in report['agent_health'].items():
                status_icon = "✅" if status == "healthy" else "❌"
                print(f"   {status_icon} {agent_name}: {status}")
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='AI Career Agent - Automated Job Applications')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Resume processing command
    resume_parser = subparsers.add_parser('process-resume', help='Process a resume file')
    resume_parser.add_argument('file', help='Path to resume file (PDF, DOCX, or TXT)')
    resume_parser.add_argument('--no-interactive', action='store_true', help='Skip interactive validation')
    
    # Job discovery command
    jobs_parser = subparsers.add_parser('discover-jobs', help='Discover job opportunities')
    jobs_parser.add_argument('--keyword', help='Job search keyword')
    jobs_parser.add_argument('--location', help='Job location')
    jobs_parser.add_argument('--category', help='Job category')
    
    # Full workflow command
    workflow_parser = subparsers.add_parser('run-workflow', help='Run full job application workflow')
    workflow_parser.add_argument('resume', help='Path to resume file')
    workflow_parser.add_argument('--keyword', help='Job search keyword')
    workflow_parser.add_argument('--location', help='Job location')
    workflow_parser.add_argument('--category', help='Job category')
    
    # Batch processing command
    batch_parser = subparsers.add_parser('batch-process', help='Process multiple resumes')
    batch_parser.add_argument('directory', help='Directory containing resume files')
    
    # Report command
    subparsers.add_parser('report', help='Generate system performance report')
    
    # Continuous mode command
    subparsers.add_parser('run', help='Run agent in continuous mode')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = CareerAgentCLI()
    
    try:
        if args.command == 'process-resume':
            asyncio.run(cli.process_resume(args.file, not args.no_interactive))
        
        elif args.command == 'discover-jobs':
            search_params = {}
            if args.keyword:
                search_params['keyword'] = args.keyword
            if args.location:
                search_params['location'] = args.location
            if args.category:
                search_params['category'] = args.category
            
            asyncio.run(cli.discover_jobs(search_params if search_params else None))
        
        elif args.command == 'run-workflow':
            search_params = {}
            if args.keyword:
                search_params['keyword'] = args.keyword
            if args.location:
                search_params['location'] = args.location
            if args.category:
                search_params['category'] = args.category
            
            asyncio.run(cli.run_full_workflow(args.resume, search_params if search_params else None))
        
        elif args.command == 'batch-process':
            asyncio.run(cli.batch_process_resumes(args.directory))
        
        elif args.command == 'report':
            asyncio.run(cli.generate_report())
        
        elif args.command == 'run':
            print("🚀 Starting AI Career Agent in continuous mode...")
            print("Press Ctrl+C to stop")
            asyncio.run(cli.orchestrator.run())
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye! Agent stopped.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()