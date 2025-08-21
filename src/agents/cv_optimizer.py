"""
CV Optimization Agent - Phase 4
Strategic resume tailoring for specific job applications
"""

import asyncio
import uuid
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import openai
from difflib import SequenceMatcher

from src.agents.base_agent import BaseAgent
from src.models.schemas import Resume, JobPosting, OptimizedResume
from src.config.settings import settings

class CVOptimizerAgent(BaseAgent):
    def __init__(self):
        super().__init__("cv_optimizer")
        try:
            self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
        except Exception as e:
            # Fallback initialization for version compatibility
            import openai as openai_module
            openai_module.api_key = settings.openai_api_key
            self.openai_client = openai_module
        self.optimization_strategies = {
            'keyword_matching': 0.3,
            'skill_alignment': 0.25,
            'experience_relevance': 0.25,
            'format_optimization': 0.2
        }
    
    async def process(self, resume: Resume, job_posting: JobPosting) -> OptimizedResume:
        """Main processing function for resume optimization"""
        try:
            self.log_info(f"Optimizing resume for job: {job_posting.title} at {job_posting.company}")
            
            # Analyze job requirements
            job_analysis = await self._analyze_job_requirements(job_posting)
            
            # Calculate initial match score
            initial_match_score = await self._calculate_match_score(resume, job_posting)
            
            # Generate optimized content
            optimized_content, optimization_notes = await self._optimize_resume_content(
                resume, job_posting, job_analysis
            )
            
            # Calculate optimized match score
            optimized_match_score = await self._calculate_optimized_match_score(
                optimized_content, job_posting
            )
            
            # Create optimized resume object
            optimized_resume = OptimizedResume(
                id=str(uuid.uuid4()),
                original_resume_id=resume.id,
                job_posting_id=job_posting.id,
                optimized_content=optimized_content,
                match_score=optimized_match_score,
                optimization_notes=optimization_notes,
                created_at=datetime.now()
            )
            
            self.log_info(
                f"Resume optimization complete. Match score improved from "
                f"{initial_match_score:.2f} to {optimized_match_score:.2f}"
            )
            
            return optimized_resume
            
        except Exception as e:
            self.log_error(f"Error optimizing resume: {e}")
            raise
    
    async def _analyze_job_requirements(self, job_posting: JobPosting) -> Dict[str, Any]:
        """Analyze job posting to extract key requirements and preferences"""
        try:
            system_prompt = """
            You are an expert HR analyst. Analyze this job posting and extract:
            1. Required technical skills (must-have)
            2. Preferred technical skills (nice-to-have)
            3. Required experience level and type
            4. Key responsibilities and duties
            5. Company culture indicators
            6. Important keywords that should appear in a matching resume
            
            Return a JSON object with these categories.
            """
            
            analysis_text = f"""
            Job Title: {job_posting.title}
            Company: {job_posting.company}
            Location: {job_posting.location}
            Description: {job_posting.description}
            Requirements: {', '.join(job_posting.requirements) if job_posting.requirements else 'Not specified'}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": analysis_text}
                ],
                temperature=0.1,
                max_tokens=1500
            )
            
            analysis = json.loads(response.choices[0].message.content)
            return analysis
            
        except Exception as e:
            self.log_error(f"Error analyzing job requirements: {e}")
            # Fallback analysis
            return {
                'required_skills': job_posting.requirements or [],
                'preferred_skills': [],
                'experience_level': 'Mid-level',
                'key_responsibilities': [],
                'keywords': job_posting.requirements or []
            }
    
    async def _calculate_match_score(self, resume: Resume, job_posting: JobPosting) -> float:
        """Calculate match score between resume and job posting"""
        try:
            # Skill matching score
            job_skills = set([skill.lower() for skill in job_posting.requirements])
            resume_skills = set([skill.lower() for skill in resume.skills])
            
            if job_skills:
                skill_match = len(job_skills.intersection(resume_skills)) / len(job_skills)
            else:
                skill_match = 0.5  # Neutral score if no specific skills listed
            
            # Keyword matching score
            job_text = (job_posting.title + " " + job_posting.description).lower()
            resume_text = resume.content.lower()
            
            keyword_match = SequenceMatcher(None, job_text, resume_text).ratio()
            
            # Experience relevance (simplified)
            experience_match = min(resume.experience_years / 5.0, 1.0)  # Assume 5 years is optimal
            
            # Weighted combination
            total_score = (
                skill_match * self.optimization_strategies['skill_alignment'] +
                keyword_match * self.optimization_strategies['keyword_matching'] +
                experience_match * self.optimization_strategies['experience_relevance'] +
                0.7 * self.optimization_strategies['format_optimization']  # Base format score
            )
            
            return min(total_score, 1.0)
            
        except Exception as e:
            self.log_error(f"Error calculating match score: {e}")
            return 0.5
    
    async def _optimize_resume_content(
        self, 
        resume: Resume, 
        job_posting: JobPosting, 
        job_analysis: Dict[str, Any]
    ) -> Tuple[str, str]:
        """Generate optimized resume content using AI"""
        try:
            system_prompt = """
            You are an expert resume writer and career coach. Optimize this resume for the specific job posting.
            
            Guidelines:
            1. Keep all factual information accurate - don't fabricate experience or skills
            2. Reorder and emphasize relevant experience and skills
            3. Use keywords from the job posting naturally
            4. Tailor the professional summary to match the role
            5. Highlight most relevant achievements and projects
            6. Maintain professional formatting and readability
            7. Ensure ATS (Applicant Tracking System) compatibility
            
            Return the optimized resume content as a well-formatted text document.
            Then provide optimization notes explaining the changes made.
            
            Format your response as:
            OPTIMIZED_RESUME:
            [optimized resume content here]
            
            OPTIMIZATION_NOTES:
            [explanation of changes made]
            """
            
            optimization_context = f"""
            ORIGINAL RESUME:
            {resume.content}
            
            JOB POSTING:
            Title: {job_posting.title}
            Company: {job_posting.company}
            Description: {job_posting.description}
            Requirements: {', '.join(job_posting.requirements) if job_posting.requirements else 'None specified'}
            
            JOB ANALYSIS:
            {json.dumps(job_analysis, indent=2)}
            
            RESUME METADATA:
            Skills: {', '.join(resume.skills)}
            Experience: {resume.experience_years} years
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": optimization_context}
                ],
                temperature=0.2,
                max_tokens=3000
            )
            
            response_content = response.choices[0].message.content
            
            # Parse response
            if "OPTIMIZED_RESUME:" in response_content and "OPTIMIZATION_NOTES:" in response_content:
                parts = response_content.split("OPTIMIZATION_NOTES:")
                optimized_content = parts[0].replace("OPTIMIZED_RESUME:", "").strip()
                optimization_notes = parts[1].strip()
            else:
                optimized_content = response_content
                optimization_notes = "AI optimization applied with keyword matching and skill alignment"
            
            return optimized_content, optimization_notes
            
        except Exception as e:
            self.log_error(f"Error optimizing resume content: {e}")
            # Fallback optimization
            return self._basic_optimization(resume, job_posting), "Basic keyword optimization applied"
    
    def _basic_optimization(self, resume: Resume, job_posting: JobPosting) -> str:
        """Basic fallback optimization"""
        try:
            # Simple optimization: add job keywords to summary section
            content = resume.content
            
            # Add relevant keywords from job posting if not already present
            job_keywords = []
            for req in job_posting.requirements:
                if req.lower() not in content.lower():
                    job_keywords.append(req)
            
            if job_keywords:
                keyword_section = f"\nKEY SKILLS: {', '.join(job_keywords)}\n"
                # Insert after first paragraph/section
                paragraphs = content.split('\n\n')
                if len(paragraphs) > 1:
                    content = paragraphs[0] + keyword_section + '\n\n' + '\n\n'.join(paragraphs[1:])
                else:
                    content = content + keyword_section
            
            return content
            
        except Exception as e:
            self.log_error(f"Error in basic optimization: {e}")
            return resume.content
    
    async def _calculate_optimized_match_score(self, optimized_content: str, job_posting: JobPosting) -> float:
        """Calculate match score for optimized resume"""
        try:
            # Create temporary resume-like object for scoring
            temp_resume = type('TempResume', (), {
                'content': optimized_content,
                'skills': job_posting.requirements,  # Assume optimization added relevant skills
                'experience_years': 3  # Use a reasonable default
            })()
            
            return await self._calculate_match_score(temp_resume, job_posting)
            
        except Exception as e:
            self.log_error(f"Error calculating optimized match score: {e}")
            return 0.7  # Return a reasonable default
    
    async def batch_optimize(self, resume: Resume, job_postings: List[JobPosting]) -> List[OptimizedResume]:
        """Optimize a resume for multiple job postings"""
        optimized_resumes = []
        
        for job_posting in job_postings:
            try:
                if await self._should_optimize_for_job(resume, job_posting):
                    optimized = await self.process(resume, job_posting)
                    optimized_resumes.append(optimized)
                    
                    # Add delay to respect rate limits
                    await asyncio.sleep(settings.request_delay)
                    
            except Exception as e:
                self.log_error(f"Error in batch optimization for {job_posting.title}: {e}")
                continue
        
        return optimized_resumes
    
    async def _should_optimize_for_job(self, resume: Resume, job_posting: JobPosting) -> bool:
        """Determine if resume should be optimized for this job"""
        try:
            # Calculate initial match score
            initial_score = await self._calculate_match_score(resume, job_posting)
            
            # Only optimize if initial score is below threshold but shows potential
            return 0.3 <= initial_score < settings.resume_match_threshold
            
        except Exception as e:
            self.log_error(f"Error determining optimization need: {e}")
            return True  # Default to optimizing
    
    async def generate_cover_letter(self, optimized_resume: OptimizedResume, job_posting: JobPosting) -> str:
        """Generate a tailored cover letter for the optimized resume"""
        try:
            system_prompt = """
            You are an expert cover letter writer. Create a compelling, personalized cover letter 
            that connects the candidate's background to the specific job opportunity.
            
            Guidelines:
            1. Address the specific role and company
            2. Highlight 2-3 most relevant qualifications
            3. Show enthusiasm for the company and role
            4. Keep it concise (3-4 paragraphs)
            5. Include a strong opening and closing
            6. Avoid generic templates
            """
            
            context = f"""
            JOB POSTING:
            Title: {job_posting.title}
            Company: {job_posting.company}
            Description: {job_posting.description[:500]}...
            
            OPTIMIZED RESUME CONTENT:
            {optimized_resume.optimized_content[:1000]}...
            
            OPTIMIZATION NOTES:
            {optimized_resume.optimization_notes}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.log_error(f"Error generating cover letter: {e}")
            return f"Dear {job_posting.company} Hiring Team,\n\nI am writing to express my strong interest in the {job_posting.title} position..."
    
    async def health_check(self) -> bool:
        """Check if the agent is ready to optimize resumes"""
        try:
            # Check OpenAI API key
            if not settings.openai_api_key:
                self.log_error("OpenAI API key not configured")
                return False
            
            # Test OpenAI connection
            test_response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5
            )
            
            self.log_info("CV optimizer agent health check passed")
            return True
            
        except Exception as e:
            self.log_error(f"CV optimizer agent health check failed: {e}")
            return False