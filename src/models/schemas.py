"""
Data models and schemas for the job application system
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    DISCOVERED = "discovered"
    APPLIED = "applied"
    REJECTED = "rejected"
    INTERVIEW = "interview"
    OFFER = "offer"

class ApplicationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class Resume(BaseModel):
    id: str
    file_path: str
    content: str
    skills: List[str]
    experience_years: int
    education: List[Dict[str, Any]]
    work_history: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

class JobPosting(BaseModel):
    id: str
    title: str
    company: str
    location: str
    description: str
    requirements: List[str]
    salary_range: Optional[str] = None
    url: str
    discovered_at: datetime
    status: JobStatus = JobStatus.DISCOVERED

class OptimizedResume(BaseModel):
    original_resume_id: str
    job_posting_id: str
    optimized_content: str
    match_score: float
    optimization_notes: str
    created_at: datetime

class Application(BaseModel):
    id: str
    job_posting_id: str
    resume_id: str
    cover_letter: Optional[str] = None
    status: ApplicationStatus
    submitted_at: Optional[datetime] = None
    notes: Optional[str] = None