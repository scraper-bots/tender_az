"""
Database utilities for storing job application data
"""

import sqlite3
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from src.models.schemas import JobPosting, Resume, Application, OptimizedResume
from src.config.settings import settings
import json

class DatabaseManager:
    def __init__(self, db_path: str = "job_applications.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Resumes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resumes (
                id TEXT PRIMARY KEY,
                file_path TEXT NOT NULL,
                content TEXT NOT NULL,
                skills TEXT NOT NULL,
                experience_years INTEGER,
                education TEXT,
                work_history TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        
        # Job postings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_postings (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT,
                description TEXT,
                requirements TEXT,
                salary_range TEXT,
                url TEXT UNIQUE,
                discovered_at TIMESTAMP,
                status TEXT DEFAULT 'discovered'
            )
        """)
        
        # Applications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id TEXT PRIMARY KEY,
                job_posting_id TEXT,
                resume_id TEXT,
                cover_letter TEXT,
                status TEXT DEFAULT 'pending',
                submitted_at TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (job_posting_id) REFERENCES job_postings (id),
                FOREIGN KEY (resume_id) REFERENCES resumes (id)
            )
        """)
        
        # Optimized resumes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS optimized_resumes (
                id TEXT PRIMARY KEY,
                original_resume_id TEXT,
                job_posting_id TEXT,
                optimized_content TEXT,
                match_score REAL,
                optimization_notes TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY (original_resume_id) REFERENCES resumes (id),
                FOREIGN KEY (job_posting_id) REFERENCES job_postings (id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_job_posting(self, job: JobPosting) -> bool:
        """Save a job posting to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO job_postings 
                (id, title, company, location, description, requirements, salary_range, url, discovered_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job.id, job.title, job.company, job.location, job.description,
                json.dumps(job.requirements), job.salary_range, job.url,
                job.discovered_at, job.status
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving job posting: {e}")
            return False
    
    def get_pending_applications(self) -> List[Dict[str, Any]]:
        """Get all pending applications"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT a.*, j.title, j.company, j.url
            FROM applications a
            JOIN job_postings j ON a.job_posting_id = j.id
            WHERE a.status = 'pending'
        """)
        
        results = cursor.fetchall()
        conn.close()
        return [dict(zip([col[0] for col in cursor.description], row)) for row in results]