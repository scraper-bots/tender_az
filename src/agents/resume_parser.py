"""
Resume Parser Agent - Phase 2
Intelligent document parsing with user interaction capabilities
"""

import asyncio
import uuid
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import openai
from pathlib import Path

import PyPDF2
import pdfplumber
from docx import Document
from loguru import logger

from src.agents.base_agent import BaseAgent
from src.models.schemas import Resume
from src.config.settings import settings

class ResumeParserAgent(BaseAgent):
    def __init__(self):
        super().__init__("resume_parser")
        self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
        self.supported_formats = ['.pdf', '.docx', '.doc', '.txt']
    
    async def process(self, file_path: str) -> Resume:
        """Main processing function for resume parsing"""
        try:
            self.log_info(f"Starting to process resume: {file_path}")
            
            # Extract text from file
            text_content = await self._extract_text(file_path)
            
            # Parse with AI
            parsed_data = await self._parse_with_ai(text_content)
            
            # Create resume object
            resume = Resume(
                id=str(uuid.uuid4()),
                file_path=file_path,
                content=text_content,
                skills=parsed_data.get('skills', []),
                experience_years=parsed_data.get('experience_years', 0),
                education=parsed_data.get('education', []),
                work_history=parsed_data.get('work_history', []),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.log_info(f"Successfully parsed resume with {len(resume.skills)} skills")
            return resume
            
        except Exception as e:
            self.log_error(f"Error processing resume {file_path}: {e}")
            raise
    
    async def _extract_text(self, file_path: str) -> str:
        """Extract text from various file formats"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Resume file not found: {file_path}")
        
        file_ext = file_path.suffix.lower()
        
        if file_ext not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        try:
            if file_ext == '.pdf':
                return await self._extract_pdf_text(file_path)
            elif file_ext in ['.docx', '.doc']:
                return await self._extract_docx_text(file_path)
            elif file_ext == '.txt':
                return await self._extract_txt_text(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
                
        except Exception as e:
            self.log_error(f"Error extracting text from {file_path}: {e}")
            raise
    
    async def _extract_pdf_text(self, file_path: Path) -> str:
        """Extract text from PDF using multiple methods"""
        text_content = ""
        
        # Try pdfplumber first (better for complex layouts)
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n"
        except Exception as e:
            self.log_warning(f"pdfplumber failed, trying PyPDF2: {e}")
            
            # Fallback to PyPDF2
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text_content += page.extract_text() + "\n"
            except Exception as e2:
                self.log_error(f"Both PDF extraction methods failed: {e2}")
                raise
        
        return text_content.strip()
    
    async def _extract_docx_text(self, file_path: Path) -> str:
        """Extract text from DOCX files"""
        try:
            doc = Document(file_path)
            text_content = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_content.append(paragraph.text.strip())
            
            return "\n".join(text_content)
        except Exception as e:
            self.log_error(f"Error extracting DOCX text: {e}")
            raise
    
    async def _extract_txt_text(self, file_path: Path) -> str:
        """Extract text from plain text files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
    
    async def _parse_with_ai(self, text_content: str) -> Dict[str, Any]:
        """Use OpenAI to intelligently parse resume content"""
        try:
            system_prompt = """
            You are an expert resume parser. Extract structured information from the resume text.
            Return a JSON object with the following fields:
            - skills: Array of technical and professional skills
            - experience_years: Total years of professional experience (integer)
            - education: Array of education entries with degree, institution, year
            - work_history: Array of work experience with company, position, duration, responsibilities
            - contact_info: Object with email, phone, location if available
            - summary: Brief professional summary
            
            Be accurate and comprehensive. If information is unclear, make reasonable inferences.
            """
            
            user_prompt = f"Parse this resume:\n\n{text_content}"
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            parsed_json = json.loads(response.choices[0].message.content)
            
            # Validate and clean the parsed data
            return self._validate_parsed_data(parsed_json)
            
        except json.JSONDecodeError as e:
            self.log_error(f"Error parsing AI response as JSON: {e}")
            return self._fallback_parsing(text_content)
        except Exception as e:
            self.log_error(f"Error in AI parsing: {e}")
            return self._fallback_parsing(text_content)
    
    def _validate_parsed_data(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean parsed resume data"""
        validated = {
            'skills': [],
            'experience_years': 0,
            'education': [],
            'work_history': [],
            'contact_info': {},
            'summary': ''
        }
        
        # Validate skills
        if 'skills' in parsed_data and isinstance(parsed_data['skills'], list):
            validated['skills'] = [str(skill) for skill in parsed_data['skills'] if skill]
        
        # Validate experience years
        if 'experience_years' in parsed_data:
            try:
                validated['experience_years'] = max(0, int(parsed_data['experience_years']))
            except (ValueError, TypeError):
                validated['experience_years'] = 0
        
        # Validate education
        if 'education' in parsed_data and isinstance(parsed_data['education'], list):
            validated['education'] = parsed_data['education']
        
        # Validate work history
        if 'work_history' in parsed_data and isinstance(parsed_data['work_history'], list):
            validated['work_history'] = parsed_data['work_history']
        
        # Validate contact info
        if 'contact_info' in parsed_data and isinstance(parsed_data['contact_info'], dict):
            validated['contact_info'] = parsed_data['contact_info']
        
        # Validate summary
        if 'summary' in parsed_data and isinstance(parsed_data['summary'], str):
            validated['summary'] = parsed_data['summary']
        
        return validated
    
    def _fallback_parsing(self, text_content: str) -> Dict[str, Any]:
        """Fallback parsing method using basic text analysis"""
        self.log_warning("Using fallback parsing method")
        
        # Basic skill extraction (common technical skills)
        common_skills = [
            'Python', 'JavaScript', 'Java', 'C++', 'C#', 'PHP', 'Ruby', 'Go', 'Rust',
            'React', 'Vue', 'Angular', 'Node.js', 'Django', 'Flask', 'Spring',
            'SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes',
            'Git', 'Linux', 'HTML', 'CSS', 'REST', 'GraphQL'
        ]
        
        found_skills = []
        text_upper = text_content.upper()
        
        for skill in common_skills:
            if skill.upper() in text_upper:
                found_skills.append(skill)
        
        # Basic experience estimation (look for years mentioned)
        import re
        year_patterns = re.findall(r'(\d+)[\s+]?(?:years?|yrs?)', text_content.lower())
        experience_years = max([int(year) for year in year_patterns], default=0)
        
        return {
            'skills': found_skills,
            'experience_years': experience_years,
            'education': [],
            'work_history': [],
            'contact_info': {},
            'summary': ''
        }
    
    async def interactive_validation(self, resume: Resume) -> Resume:
        """Allow user to validate and correct parsed information"""
        self.log_info("Starting interactive validation")
        
        print(f"\n📄 Resume Parsed: {resume.file_path}")
        print(f"📊 Skills found: {len(resume.skills)}")
        print(f"⏱️  Experience: {resume.experience_years} years")
        
        if resume.skills:
            print(f"🔧 Skills: {', '.join(resume.skills[:10])}")
            if len(resume.skills) > 10:
                print(f"   ... and {len(resume.skills) - 10} more")
        
        # In a real implementation, you could add interactive prompts here
        # For now, we'll just log the information
        
        return resume
    
    async def health_check(self) -> bool:
        """Check if the agent is ready to process resumes"""
        try:
            # Check OpenAI API key
            if not settings.openai_api_key:
                self.log_error("OpenAI API key not configured")
                return False
            
            # Test OpenAI connection
            test_response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            self.log_info("Resume parser agent health check passed")
            return True
            
        except Exception as e:
            self.log_error(f"Resume parser agent health check failed: {e}")
            return False