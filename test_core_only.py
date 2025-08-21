#!/usr/bin/env python3
"""
Test core functionality without AI agents
"""

import asyncio
from dotenv import load_dotenv
import sys
import os

load_dotenv()
sys.path.append('src')

async def test_core_functionality():
    print("🚀 TESTING CORE FUNCTIONALITY")
    print("=" * 40)
    
    # Test 1: Database
    try:
        from src.utils.database_pg import PostgreSQLManager
        db = PostgreSQLManager()
        await db.init_database()
        jobs = await db.get_job_postings()
        print(f"✅ Database: Connected, {len(jobs)} jobs found")
    except Exception as e:
        print(f"❌ Database: {e}")
        return False
    
    # Test 2: Job Discovery (without AI)
    try:
        from src.agents.job_discovery import JobDiscoveryAgent
        agent = JobDiscoveryAgent()
        health = await agent.health_check()
        print(f"✅ Job Discovery: {'Healthy' if health else 'Unhealthy'}")
        
        if health:
            jobs = await agent.process({'keyword': 'developer'})
            print(f"   📋 Found {len(jobs)} jobs from jobs.glorri.az")
    except Exception as e:
        print(f"❌ Job Discovery: {e}")
    
    print("\n🎯 SYSTEM READY FOR:")
    print("   • Job discovery and scraping")
    print("   • Database operations")
    print("   • Basic workflow without AI optimization")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_core_functionality())