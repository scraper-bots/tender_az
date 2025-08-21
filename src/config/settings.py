"""
Configuration settings for the job application agent
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Database
    database_url: str = "postgresql://username:password@hostname:port/database"
    database_schema: str = "careeragent"
    
    # Web scraping
    selenium_headless: bool = True
    request_delay: float = 1.0
    max_retries: int = 3
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/agent.log"
    
    # Application settings
    max_applications_per_day: int = 10
    resume_match_threshold: float = 0.7
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()