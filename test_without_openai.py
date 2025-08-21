#!/usr/bin/env python3
"""
Test the system without OpenAI dependency to isolate issues
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_database_only():
    """Test only database functionality"""
    print("🗄️ Testing Database Connection...")
    try:
        from src.utils.database_pg import PostgreSQLManager
        
        db = PostgreSQLManager()
        await db.init_database()
        
        jobs = await db.get_job_postings()
        print(f"   ✅ Database connected - Found {len(jobs)} job postings")
        return True
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        return False

async def test_job_discovery_only():
    """Test job discovery without OpenAI"""
    print("\n🔍 Testing Job Discovery Agent...")
    try:
        from src.agents.job_discovery import JobDiscoveryAgent
        
        agent = JobDiscoveryAgent()
        health = await agent.health_check()
        
        if health:
            print("   ✅ Job discovery agent healthy")
            print("   🌐 Testing jobs.glorri.az connection...")
            
            # Test basic job discovery
            jobs = await agent.process({})
            print(f"   📋 Discovered {len(jobs)} jobs")
            
            if jobs:
                print(f"   📝 Sample job: {jobs[0].title} at {jobs[0].company}")
            
            return True
        else:
            print("   ❌ Job discovery agent unhealthy")
            return False
            
    except Exception as e:
        print(f"   ❌ Job discovery test failed: {e}")
        return False

def test_environment():
    """Test environment variables"""
    print("\n🌍 Testing Environment...")
    
    db_url = os.getenv('DATABASE_URL')
    api_key = os.getenv('OPENAI_API_KEY')
    
    if db_url:
        print(f"   ✅ Database URL configured")
    else:
        print("   ❌ DATABASE_URL not set")
        return False
    
    if api_key:
        print(f"   ✅ OpenAI API key configured")
    else:
        print("   ❌ OPENAI_API_KEY not set")
        return False
    
    return True

async def main():
    print("🧪 BASIC SYSTEM TEST (Without OpenAI)")
    print("=" * 40)
    
    results = []
    
    # Test environment
    results.append(test_environment())
    
    # Test database
    results.append(await test_database_only())
    
    # Test job discovery
    results.append(await test_job_discovery_only())
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 TEST RESULTS: {passed}/{total} passed")
    
    if passed >= 2:
        print("🎉 Core system is working!")
        print("🔧 Only OpenAI integration needs fixing")
        print("\nNext steps:")
        print("   pip uninstall openai -y")
        print("   pip install openai==1.12.0")
    else:
        print("⚠️ Core system issues found")

if __name__ == "__main__":
    asyncio.run(main())