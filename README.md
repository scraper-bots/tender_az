# AI Job Application Agent

An intelligent multi-agent system that automates the job application process through specialized AI agents.

## Overview

This system consists of multiple specialized agents working together:

1. **Orchestrator Agent** - Coordinates all other agents
2. **Resume Parser Agent** - Intelligently parses and analyzes resumes
3. **Job Discovery Agent** - Scrapes and discovers job opportunities
4. **CV Optimization Agent** - Tailors resumes for specific jobs
5. **Application Agent** - Submits applications automatically
6. **Learning Agent** - Continuously improves the system

## Project Structure

```
career-agent/
├── src/
│   ├── agents/          # Specialized AI agents
│   ├── config/          # Configuration and settings
│   ├── models/          # Data models and schemas
│   └── utils/           # Utility functions
├── main.py              # Main entry point
├── requirements.txt     # Python dependencies
└── README.md
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run the agent:**
   ```bash
   # Simple mode
   python main.py
   
   # CLI mode with commands
   python cli.py --help
   
   # Examples:
   python cli.py process-resume path/to/resume.pdf
   python cli.py discover-jobs --keyword "software engineer"
   python cli.py run-workflow resume.pdf --keyword "python developer"
   python cli.py run  # Continuous mode
   ```

## Implementation Phases

- ✅ **Phase 1**: Foundation Setup - Basic infrastructure and orchestrator
- ✅ **Phase 2**: Resume Parser Agent - Document parsing and analysis  
- ✅ **Phase 3**: Job Discovery Agent - Web scraping for jobs.glorri.az
- ✅ **Phase 4**: CV Optimization Agent - Strategic resume tailoring
- ✅ **Phase 5**: Application Agent - Intelligent form submission
- ✅ **Phase 6**: Integration & Learning - Multi-agent coordination

## Features

- **🤖 Multi-Agent Architecture**: Specialized AI agents for each task
- **📄 Intelligent Resume Parsing**: Extract skills, experience, and details from PDF/DOCX
- **🔍 Job Discovery**: Adaptive scraping of jobs.glorri.az with smart filtering
- **⚡ CV Optimization**: AI-powered resume tailoring for specific jobs  
- **🚀 Auto Application**: Intelligent form submission with selenium automation
- **📊 Analytics Dashboard**: Track success rates and performance metrics
- **🗄️ Database Integration**: PostgreSQL with careeragent schema
- **🌐 Web Frontend**: Next.js interface with Vercel deployment
- **📱 CLI Interface**: Command-line tools for all operations

## Agent Capabilities

### Resume Parser Agent
- Supports PDF, DOCX, and TXT files
- Extracts skills, experience, education, contact info
- AI-powered content analysis with fallback parsing
- Interactive validation and correction

### Job Discovery Agent  
- Adaptive scraping of jobs.glorri.az
- Multiple selector strategies for different page layouts
- Rate limiting and error handling
- Job deduplication and filtering

### CV Optimizer Agent
- Strategic resume tailoring using GPT-4
- Keyword optimization and ATS compatibility
- Match score calculation and improvement tracking
- Cover letter generation

### Application Agent
- Intelligent form detection and filling
- File upload handling for resumes
- Authorization question answering
- Submission confirmation detection

## CLI Usage

```bash
# Process a single resume
python cli.py process-resume path/to/resume.pdf

# Discover jobs with filters
python cli.py discover-jobs --keyword "python developer" --location "remote"

# Run complete workflow
python cli.py run-workflow resume.pdf --keyword "software engineer"

# Batch process multiple resumes
python cli.py batch-process /path/to/resume/directory

# Generate performance report
python cli.py report

# Run in continuous mode
python cli.py run
```

## Requirements

- Python 3.8+
- OpenAI API access (GPT-4 recommended)
- PostgreSQL database with careeragent schema
- Chrome browser for Selenium automation
- Node.js 18+ (for frontend)