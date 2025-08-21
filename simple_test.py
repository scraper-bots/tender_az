#!/usr/bin/env python3
"""
Simple test to verify basic functionality
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that we can import all modules"""
    print("🔧 Testing imports...")
    
    try:
        from src.config.settings import settings
        print("   ✅ Settings imported")
    except Exception as e:
        print(f"   ❌ Settings failed: {e}")
        return False
    
    try:
        from src.agents.resume_parser import ResumeParserAgent
        print("   ✅ Resume parser imported")
    except Exception as e:
        print(f"   ❌ Resume parser failed: {e}")
        return False
    
    try:
        from src.orchestrator import JobApplicationOrchestrator
        print("   ✅ Orchestrator imported")
    except Exception as e:
        print(f"   ❌ Orchestrator failed: {e}")
        return False
    
    return True

def test_environment():
    """Test environment configuration"""
    print("\n🌍 Testing environment...")
    
    db_url = os.getenv('DATABASE_URL')
    api_key = os.getenv('OPENAI_API_KEY')
    
    if db_url:
        print(f"   ✅ Database URL configured ({db_url[:30]}...)")
    else:
        print("   ❌ DATABASE_URL not set")
        return False
    
    if api_key:
        print(f"   ✅ OpenAI API key configured ({api_key[:20]}...)")
    else:
        print("   ❌ OPENAI_API_KEY not set")
        return False
    
    return True

async def test_basic_functionality():
    """Test basic agent functionality"""
    print("\n🤖 Testing basic functionality...")
    
    try:
        from src.orchestrator import JobApplicationOrchestrator
        
        orchestrator = JobApplicationOrchestrator()
        print("   ✅ Orchestrator created")
        
        # Try to start agents (this will test database connection)
        await orchestrator.start_agents()
        print("   ✅ Agents started")
        
        # Generate report
        report = await orchestrator.generate_performance_report()
        print(f"   ✅ Report generated")
        
        # Check agent health
        healthy_count = sum(1 for status in report['agent_health'].values() 
                          if 'healthy' in status.lower())
        print(f"   📊 {healthy_count}/4 agents healthy")
        
        return healthy_count >= 2  # At least half should be healthy
        
    except Exception as e:
        print(f"   ❌ Basic functionality failed: {e}")
        return False

def main():
    print("🧪 SIMPLE TEST SUITE")
    print("=" * 30)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed - install dependencies:")
        print("   pip install pydantic-settings")
        return False
    
    # Test environment  
    if not test_environment():
        print("\n❌ Environment tests failed - check .env file")
        return False
    
    # Test basic functionality
    import asyncio
    if asyncio.run(test_basic_functionality()):
        print("\n🎉 ALL TESTS PASSED!")
        print("\n🎯 You can now run:")
        print("   python cli.py report")
        print("   python cli.py discover-jobs")
        print("   python main.py")
        return True
    else:
        print("\n⚠️ Some functionality issues - check database connection")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)