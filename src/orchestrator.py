"""
Main orchestrator that coordinates all agents - Phase 6 Integration
"""

import asyncio
from typing import Dict, List, Any, Optional
from loguru import logger
from pathlib import Path

from src.agents.base_agent import BaseAgent
from src.agents.resume_parser import ResumeParserAgent
from src.agents.job_discovery import JobDiscoveryAgent
from src.agents.cv_optimizer import CVOptimizerAgent
from src.agents.application_agent import ApplicationAgent
from src.utils.database_pg import PostgreSQLManager
from src.models.schemas import Resume, JobPosting, OptimizedResume, Application
from src.config.settings import settings

class JobApplicationOrchestrator:
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.logger = logger.bind(component="orchestrator")
        self.is_running = False
        self.db_manager = PostgreSQLManager()
        
        # Initialize all agents
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize and register all agents"""
        self.resume_parser = ResumeParserAgent()
        self.job_discovery = JobDiscoveryAgent()
        self.cv_optimizer = CVOptimizerAgent()
        self.application_agent = ApplicationAgent()
        
        # Register agents
        self.register_agent(self.resume_parser)
        self.register_agent(self.job_discovery)
        self.register_agent(self.cv_optimizer)
        self.register_agent(self.application_agent)
    
    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the orchestrator"""
        self.agents[agent.name] = agent
        self.logger.info(f"Registered agent: {agent.name}")
    
    async def start_agents(self) -> None:
        """Initialize and start all registered agents"""
        self.logger.info("Starting all agents...")
        
        # Initialize database
        await self.db_manager.init_database()
        self.logger.info("Database initialized")
        
        for name, agent in self.agents.items():
            try:
                health = await agent.health_check()
                if health:
                    self.logger.info(f"Agent {name} is healthy and ready")
                else:
                    self.logger.warning(f"Agent {name} failed health check")
            except Exception as e:
                self.logger.error(f"Failed to start agent {name}: {e}")
    
    async def stop_agents(self) -> None:
        """Stop all agents gracefully"""
        self.logger.info("Stopping all agents...")
        self.is_running = False
    
    async def process_resume(self, file_path: str) -> Resume:
        """Process a resume file through the resume parser agent"""
        try:
            self.logger.info(f"Processing resume: {file_path}")
            
            # Parse resume
            resume = await self.resume_parser.process(file_path)
            
            # Interactive validation
            resume = await self.resume_parser.interactive_validation(resume)
            
            # Save to database
            success = await self.db_manager.save_resume(resume)
            if success:
                self.logger.info(f"Resume saved successfully: {resume.id}")
            else:
                self.logger.error("Failed to save resume to database")
            
            return resume
            
        except Exception as e:
            self.logger.error(f"Error processing resume {file_path}: {e}")
            raise
    
    async def discover_jobs(self, search_params: Optional[Dict[str, Any]] = None) -> List[JobPosting]:
        """Discover job opportunities using the job discovery agent"""
        try:
            self.logger.info("Starting job discovery")
            
            # Discover jobs
            jobs = await self.job_discovery.process(search_params)
            
            # Save jobs to database
            saved_count = 0
            for job in jobs:
                success = await self.db_manager.save_job_posting(job)
                if success:
                    saved_count += 1
            
            self.logger.info(f"Discovered {len(jobs)} jobs, saved {saved_count} to database")
            return jobs
            
        except Exception as e:
            self.logger.error(f"Error discovering jobs: {e}")
            return []
    
    async def optimize_resume_for_job(self, resume: Resume, job_posting: JobPosting) -> OptimizedResume:
        """Optimize a resume for a specific job posting"""
        try:
            self.logger.info(f"Optimizing resume {resume.id} for job {job_posting.title}")
            
            # Optimize resume
            optimized_resume = await self.cv_optimizer.process(resume, job_posting)
            
            self.logger.info(f"Resume optimization complete. Match score: {optimized_resume.match_score:.2f}")
            return optimized_resume
            
        except Exception as e:
            self.logger.error(f"Error optimizing resume: {e}")
            raise
    
    async def submit_application(
        self, 
        optimized_resume: OptimizedResume, 
        job_posting: JobPosting,
        generate_cover_letter: bool = True
    ) -> Application:
        """Submit an application using the optimized resume"""
        try:
            self.logger.info(f"Submitting application for {job_posting.title} at {job_posting.company}")
            
            # Generate cover letter if requested
            cover_letter = None
            if generate_cover_letter:
                cover_letter = await self.cv_optimizer.generate_cover_letter(optimized_resume, job_posting)
            
            # Submit application
            application = await self.application_agent.process(
                optimized_resume, job_posting, cover_letter
            )
            
            self.logger.info(f"Application status: {application.status}")
            return application
            
        except Exception as e:
            self.logger.error(f"Error submitting application: {e}")
            raise
    
    async def full_application_workflow(self, resume_path: str, job_search_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute the complete job application workflow"""
        try:
            self.logger.info("Starting full application workflow")
            results = {
                'resume_processed': False,
                'jobs_discovered': 0,
                'applications_submitted': 0,
                'successful_applications': 0,
                'failed_applications': 0,
                'applications': []
            }
            
            # Step 1: Process Resume
            self.logger.info("Step 1: Processing resume")
            resume = await self.process_resume(resume_path)
            results['resume_processed'] = True
            
            # Step 2: Discover Jobs
            self.logger.info("Step 2: Discovering jobs")
            jobs = await self.discover_jobs(job_search_params)
            results['jobs_discovered'] = len(jobs)
            
            if not jobs:
                self.logger.warning("No jobs discovered. Stopping workflow.")
                return results
            
            # Step 3: Process Applications
            self.logger.info("Step 3: Processing applications")
            
            # Filter jobs based on match potential
            suitable_jobs = []
            for job in jobs[:settings.max_applications_per_day]:  # Respect daily limit
                # Quick compatibility check
                if await self._is_job_suitable(resume, job):
                    suitable_jobs.append(job)
            
            self.logger.info(f"Found {len(suitable_jobs)} suitable jobs out of {len(jobs)}")
            
            # Process each suitable job
            for job in suitable_jobs:
                try:
                    # Step 3a: Optimize resume for job
                    optimized_resume = await self.optimize_resume_for_job(resume, job)
                    
                    # Step 3b: Submit application if match score is good enough
                    if optimized_resume.match_score >= settings.resume_match_threshold:
                        application = await self.submit_application(optimized_resume, job)
                        results['applications'].append({
                            'job_title': job.title,
                            'company': job.company,
                            'status': application.status,
                            'match_score': optimized_resume.match_score,
                            'submitted_at': application.submitted_at
                        })
                        
                        results['applications_submitted'] += 1
                        if application.status == 'completed':
                            results['successful_applications'] += 1
                        else:
                            results['failed_applications'] += 1
                    else:
                        self.logger.info(f"Skipping {job.title} - match score too low: {optimized_resume.match_score:.2f}")
                
                except Exception as e:
                    self.logger.error(f"Error processing application for {job.title}: {e}")
                    results['failed_applications'] += 1
                
                # Rate limiting between applications
                await asyncio.sleep(settings.request_delay * 2)
            
            self.logger.info(f"Workflow complete. Submitted {results['applications_submitted']} applications")
            return results
            
        except Exception as e:
            self.logger.error(f"Error in full application workflow: {e}")
            raise
    
    async def _is_job_suitable(self, resume: Resume, job_posting: JobPosting) -> bool:
        """Quick check if a job is worth applying to"""
        try:
            # Check for basic skill overlap
            job_skills = set([skill.lower() for skill in job_posting.requirements])
            resume_skills = set([skill.lower() for skill in resume.skills])
            
            if job_skills:
                skill_overlap = len(job_skills.intersection(resume_skills)) / len(job_skills)
                return skill_overlap >= 0.2  # At least 20% skill overlap
            
            # If no specific skills listed, consider it suitable
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking job suitability: {e}")
            return True  # Default to suitable if check fails
    
    async def batch_process_resumes(self, resume_directory: str) -> List[Resume]:
        """Process multiple resumes from a directory"""
        try:
            resume_dir = Path(resume_directory)
            if not resume_dir.exists():
                raise FileNotFoundError(f"Resume directory not found: {resume_directory}")
            
            resumes = []
            resume_files = list(resume_dir.glob("*.pdf")) + list(resume_dir.glob("*.docx")) + list(resume_dir.glob("*.txt"))
            
            self.logger.info(f"Found {len(resume_files)} resume files to process")
            
            for resume_file in resume_files:
                try:
                    resume = await self.process_resume(str(resume_file))
                    resumes.append(resume)
                    
                    # Small delay between processing
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    self.logger.error(f"Error processing {resume_file}: {e}")
                    continue
            
            self.logger.info(f"Successfully processed {len(resumes)} resumes")
            return resumes
            
        except Exception as e:
            self.logger.error(f"Error in batch resume processing: {e}")
            return []
    
    async def generate_performance_report(self) -> Dict[str, Any]:
        """Generate a performance report of the system"""
        try:
            # Get data from database
            pending_applications = await self.db_manager.get_pending_applications()
            all_jobs = await self.db_manager.get_job_postings()
            
            report = {
                'timestamp': asyncio.get_event_loop().time(),
                'total_jobs_discovered': len(all_jobs),
                'pending_applications': len(pending_applications),
                'agent_health': {},
                'system_metrics': {
                    'avg_match_score': 0.0,
                    'success_rate': 0.0,
                    'jobs_per_day': 0.0
                }
            }
            
            # Check agent health
            for name, agent in self.agents.items():
                try:
                    health = await agent.health_check()
                    report['agent_health'][name] = 'healthy' if health else 'unhealthy'
                except Exception as e:
                    report['agent_health'][name] = f'error: {str(e)}'
            
            self.logger.info("Performance report generated")
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating performance report: {e}")
            return {'error': str(e)}
    
    async def process_job_application_workflow(self) -> None:
        """Main workflow for continuous job applications"""
        self.logger.info("Running continuous job application workflow")
        
        try:
            # Discover new jobs periodically
            jobs = await self.discover_jobs()
            if jobs:
                self.logger.info(f"Discovered {len(jobs)} new jobs")
            
            # Process any pending applications
            pending_applications = await self.db_manager.get_pending_applications()
            if pending_applications:
                self.logger.info(f"Found {len(pending_applications)} pending applications to process")
            
            # Generate performance report
            report = await self.generate_performance_report()
            self.logger.info(f"System status: {report['agent_health']}")
            
        except Exception as e:
            self.logger.error(f"Error in continuous workflow: {e}")
    
    async def run(self) -> None:
        """Main run loop"""
        self.is_running = True
        await self.start_agents()
        
        try:
            while self.is_running:
                await self.process_job_application_workflow()
                await asyncio.sleep(300)  # Run every 5 minutes
        except KeyboardInterrupt:
            self.logger.info("Received shutdown signal")
        finally:
            await self.stop_agents()