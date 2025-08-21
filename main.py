#!/usr/bin/env python3
"""
AI Job Application Agent - Main Entry Point
Orchestrates multiple specialized agents for job application automation
"""

import asyncio
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.orchestrator import JobApplicationOrchestrator

async def main():
    logger.info("Starting AI Job Application Agent")
    
    orchestrator = JobApplicationOrchestrator()
    await orchestrator.run()

if __name__ == "__main__":
    asyncio.run(main())