"""
PostgreSQL database utilities for the career agent
"""

import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import json
import uuid

from src.models.schemas import JobPosting, Resume, Application, OptimizedResume
from src.config.settings import settings

class PostgreSQLManager:
    def __init__(self):
        self.database_url = settings.database_url
        self.schema = settings.database_schema
        
        # Convert to async URL if needed
        if not self.database_url.startswith('postgresql+asyncpg'):
            self.async_database_url = self.database_url.replace('postgresql://', 'postgresql+asyncpg://')
        else:
            self.async_database_url = self.database_url
            
        self.engine = create_async_engine(self.async_database_url)
        self.SessionLocal = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
    
    async def init_database(self):
        """Initialize database tables in the careeragent schema"""
        async with self.engine.begin() as conn:
            # Create schema if it doesn't exist
            await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {self.schema}"))
            
            # Create tables
            await conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {self.schema}.resumes (
                    id TEXT PRIMARY KEY,
                    file_path TEXT NOT NULL,
                    content TEXT NOT NULL,
                    skills TEXT[] NOT NULL DEFAULT '{{}}',
                    experience_years INTEGER DEFAULT 0,
                    education JSONB DEFAULT '[]',
                    work_history JSONB DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            await conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {self.schema}.job_postings (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    location TEXT,
                    description TEXT,
                    requirements TEXT[] DEFAULT '{{}}',
                    salary_range TEXT,
                    url TEXT UNIQUE,
                    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'discovered'
                )
            """))
            
            await conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {self.schema}.applications (
                    id TEXT PRIMARY KEY,
                    job_posting_id TEXT REFERENCES {self.schema}.job_postings(id),
                    resume_id TEXT REFERENCES {self.schema}.resumes(id),
                    cover_letter TEXT,
                    status TEXT DEFAULT 'pending',
                    submitted_at TIMESTAMP,
                    notes TEXT
                )
            """))
            
            await conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {self.schema}.optimized_resumes (
                    id TEXT PRIMARY KEY,
                    original_resume_id TEXT REFERENCES {self.schema}.resumes(id),
                    job_posting_id TEXT REFERENCES {self.schema}.job_postings(id),
                    optimized_content TEXT,
                    match_score REAL,
                    optimization_notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
    
    async def save_job_posting(self, job: JobPosting) -> bool:
        """Save a job posting to database"""
        try:
            async with self.SessionLocal() as session:
                await session.execute(text(f"""
                    INSERT INTO {self.schema}.job_postings 
                    (id, title, company, location, description, requirements, salary_range, url, discovered_at, status)
                    VALUES (:id, :title, :company, :location, :description, :requirements, :salary_range, :url, :discovered_at, :status)
                    ON CONFLICT (url) DO UPDATE SET
                        title = EXCLUDED.title,
                        company = EXCLUDED.company,
                        location = EXCLUDED.location,
                        description = EXCLUDED.description,
                        requirements = EXCLUDED.requirements,
                        salary_range = EXCLUDED.salary_range,
                        status = EXCLUDED.status
                """), {
                    'id': job.id,
                    'title': job.title,
                    'company': job.company,
                    'location': job.location,
                    'description': job.description,
                    'requirements': job.requirements,
                    'salary_range': job.salary_range,
                    'url': job.url,
                    'discovered_at': job.discovered_at,
                    'status': job.status
                })
                await session.commit()
                return True
        except Exception as e:
            print(f"Error saving job posting: {e}")
            return False
    
    async def save_resume(self, resume: Resume) -> bool:
        """Save a resume to database"""
        try:
            async with self.SessionLocal() as session:
                await session.execute(text(f"""
                    INSERT INTO {self.schema}.resumes 
                    (id, file_path, content, skills, experience_years, education, work_history, created_at, updated_at)
                    VALUES (:id, :file_path, :content, :skills, :experience_years, :education, :work_history, :created_at, :updated_at)
                    ON CONFLICT (id) DO UPDATE SET
                        content = EXCLUDED.content,
                        skills = EXCLUDED.skills,
                        experience_years = EXCLUDED.experience_years,
                        education = EXCLUDED.education,
                        work_history = EXCLUDED.work_history,
                        updated_at = EXCLUDED.updated_at
                """), {
                    'id': resume.id,
                    'file_path': resume.file_path,
                    'content': resume.content,
                    'skills': resume.skills,
                    'experience_years': resume.experience_years,
                    'education': json.dumps(resume.education),
                    'work_history': json.dumps(resume.work_history),
                    'created_at': resume.created_at,
                    'updated_at': resume.updated_at
                })
                await session.commit()
                return True
        except Exception as e:
            print(f"Error saving resume: {e}")
            return False
    
    async def get_pending_applications(self) -> List[Dict[str, Any]]:
        """Get all pending applications"""
        try:
            async with self.SessionLocal() as session:
                result = await session.execute(text(f"""
                    SELECT a.*, j.title, j.company, j.url
                    FROM {self.schema}.applications a
                    JOIN {self.schema}.job_postings j ON a.job_posting_id = j.id
                    WHERE a.status = 'pending'
                """))
                return [dict(row._mapping) for row in result]
        except Exception as e:
            print(f"Error getting pending applications: {e}")
            return []
    
    async def get_job_postings(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get job postings, optionally filtered by status"""
        try:
            async with self.SessionLocal() as session:
                if status:
                    result = await session.execute(text(f"""
                        SELECT * FROM {self.schema}.job_postings 
                        WHERE status = :status 
                        ORDER BY discovered_at DESC
                    """), {'status': status})
                else:
                    result = await session.execute(text(f"""
                        SELECT * FROM {self.schema}.job_postings 
                        ORDER BY discovered_at DESC
                    """))
                return [dict(row._mapping) for row in result]
        except Exception as e:
            print(f"Error getting job postings: {e}")
            return []