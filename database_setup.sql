-- AI Career Agent Database Setup
-- Run this script directly in your Neon PostgreSQL database

-- ================================================
-- 1. CREATE SCHEMA
-- ================================================
CREATE SCHEMA IF NOT EXISTS careeragent;

-- ================================================
-- 2. CREATE TABLES
-- ================================================

-- Resumes table
CREATE TABLE IF NOT EXISTS careeragent.resumes (
    id TEXT PRIMARY KEY,
    file_path TEXT NOT NULL,
    content TEXT NOT NULL,
    skills TEXT[] NOT NULL DEFAULT '{}',
    experience_years INTEGER DEFAULT 0,
    education JSONB DEFAULT '[]',
    work_history JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Job postings table
CREATE TABLE IF NOT EXISTS careeragent.job_postings (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT,
    description TEXT,
    requirements TEXT[] DEFAULT '{}',
    salary_range TEXT,
    url TEXT UNIQUE,
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'discovered'
);

-- Applications table
CREATE TABLE IF NOT EXISTS careeragent.applications (
    id TEXT PRIMARY KEY,
    job_posting_id TEXT REFERENCES careeragent.job_postings(id),
    resume_id TEXT REFERENCES careeragent.resumes(id),
    cover_letter TEXT,
    status TEXT DEFAULT 'pending',
    submitted_at TIMESTAMP,
    notes TEXT
);

-- Optimized resumes table
CREATE TABLE IF NOT EXISTS careeragent.optimized_resumes (
    id TEXT PRIMARY KEY,
    original_resume_id TEXT REFERENCES careeragent.resumes(id),
    job_posting_id TEXT REFERENCES careeragent.job_postings(id),
    optimized_content TEXT,
    match_score REAL,
    optimization_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ================================================
-- 3. CREATE INDEXES FOR PERFORMANCE
-- ================================================

-- Index on job posting URLs for duplicate prevention
CREATE INDEX IF NOT EXISTS idx_job_postings_url 
ON careeragent.job_postings(url);

-- Index on application status for filtering
CREATE INDEX IF NOT EXISTS idx_applications_status 
ON careeragent.applications(status);

-- Index on job posting status
CREATE INDEX IF NOT EXISTS idx_job_postings_status 
ON careeragent.job_postings(status);

-- Index on discovered_at for chronological queries
CREATE INDEX IF NOT EXISTS idx_job_postings_discovered_at 
ON careeragent.job_postings(discovered_at DESC);

-- Index on created_at for resumes
CREATE INDEX IF NOT EXISTS idx_resumes_created_at 
ON careeragent.resumes(created_at DESC);

-- Index on optimized resumes for match score queries
CREATE INDEX IF NOT EXISTS idx_optimized_resumes_match_score 
ON careeragent.optimized_resumes(match_score DESC);

-- Index on application submitted_at for reporting
CREATE INDEX IF NOT EXISTS idx_applications_submitted_at 
ON careeragent.applications(submitted_at DESC);

-- ================================================
-- 4. INSERT SAMPLE DATA (OPTIONAL FOR TESTING)
-- ================================================

-- Sample resume for testing
INSERT INTO careeragent.resumes (
    id, 
    file_path, 
    content, 
    skills, 
    experience_years, 
    education, 
    work_history,
    created_at,
    updated_at
) VALUES (
    'sample-resume-1',
    'sample_resume.pdf',
    'John Doe
Software Engineer
john.doe@email.com
+1234567890

PROFESSIONAL SUMMARY:
Experienced software engineer with 3 years of expertise in full-stack development using Python, React, and PostgreSQL. Proven track record in building scalable web applications and working with agile development methodologies.

TECHNICAL SKILLS:
- Programming Languages: Python, JavaScript, TypeScript, SQL
- Frontend: React, HTML5, CSS3, Tailwind CSS
- Backend: Node.js, Django, FastAPI, REST APIs
- Databases: PostgreSQL, MongoDB, Redis
- Tools: Git, Docker, AWS, Linux

WORK EXPERIENCE:
Software Developer - Tech Corp (2021-2023)
- Built and maintained web applications using React and Node.js
- Designed and implemented REST APIs serving 10,000+ daily users
- Collaborated with cross-functional teams using Agile methodologies
- Optimized database queries resulting in 40% performance improvement

Junior Developer - StartupXYZ (2020-2021)
- Developed frontend components using React and JavaScript
- Worked with PostgreSQL databases and wrote complex SQL queries
- Participated in code reviews and maintained high code quality standards

EDUCATION:
Bachelor of Computer Science - Tech University (2020)
- Relevant coursework: Data Structures, Algorithms, Database Systems, Software Engineering

PROJECTS:
- E-commerce Platform: Full-stack application with React frontend and Django backend
- Task Management System: Built with Node.js and PostgreSQL, deployed on AWS',
    ARRAY['Python', 'React', 'PostgreSQL', 'JavaScript', 'Node.js', 'Django', 'REST API', 'HTML', 'CSS', 'Git', 'Docker', 'AWS'],
    3,
    '[
        {
            "degree": "Bachelor of Computer Science", 
            "institution": "Tech University", 
            "year": 2020,
            "gpa": "3.8"
        }
    ]'::jsonb,
    '[
        {
            "company": "Tech Corp", 
            "position": "Software Developer", 
            "duration": "2021-2023", 
            "responsibilities": [
                "Built and maintained web applications using React and Node.js",
                "Designed and implemented REST APIs serving 10,000+ daily users",
                "Optimized database queries resulting in 40% performance improvement"
            ]
        },
        {
            "company": "StartupXYZ", 
            "position": "Junior Developer", 
            "duration": "2020-2021", 
            "responsibilities": [
                "Developed frontend components using React and JavaScript",
                "Worked with PostgreSQL databases and wrote complex SQL queries"
            ]
        }
    ]'::jsonb,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- Sample job posting for testing
INSERT INTO careeragent.job_postings (
    id,
    title,
    company,
    location,
    description,
    requirements,
    salary_range,
    url,
    status,
    discovered_at
) VALUES (
    'sample-job-1',
    'Senior Python Developer',
    'Innovation Labs',
    'Remote',
    'We are looking for an experienced Python developer to join our dynamic team. The ideal candidate will have strong experience with Django, REST APIs, and modern development practices. You will be responsible for building scalable backend services and working closely with our frontend team to deliver exceptional user experiences.

Key Responsibilities:
- Design and develop robust backend services using Python and Django
- Build and maintain REST APIs that serve millions of requests
- Collaborate with cross-functional teams including designers and product managers
- Write clean, maintainable, and well-tested code
- Participate in code reviews and technical discussions
- Mentor junior developers and contribute to team growth

What We Offer:
- Competitive salary and equity package
- Flexible remote work arrangements
- Professional development opportunities
- Health and wellness benefits
- Modern tech stack and tools',
    ARRAY['Python', 'Django', 'PostgreSQL', 'REST API', 'Git', 'Docker', 'AWS', 'JavaScript'],
    '$80,000 - $120,000',
    'https://jobs.glorri.az/sample-job-1',
    'discovered',
    CURRENT_TIMESTAMP
);

-- Sample optimized resume
INSERT INTO careeragent.optimized_resumes (
    id,
    original_resume_id,
    job_posting_id,
    optimized_content,
    match_score,
    optimization_notes,
    created_at
) VALUES (
    'sample-optimized-1',
    'sample-resume-1',
    'sample-job-1',
    'OPTIMIZED RESUME FOR SENIOR PYTHON DEVELOPER POSITION

John Doe
Senior Python Developer
john.doe@email.com
+1234567890

PROFESSIONAL SUMMARY:
Experienced Python developer with 3+ years of expertise in Django, REST API development, and PostgreSQL. Proven track record building scalable backend services and mentoring junior developers in agile environments.

CORE TECHNICAL SKILLS:
- Python Development: Django, FastAPI, REST APIs
- Database Systems: PostgreSQL, query optimization
- DevOps & Tools: Docker, AWS, Git, Linux
- Frontend Integration: JavaScript, React
- Development Practices: Agile, Code Reviews, Testing

PROFESSIONAL EXPERIENCE:
Software Developer - Tech Corp (2021-2023)
• Built scalable REST APIs using Django serving 10,000+ daily users
• Optimized PostgreSQL queries resulting in 40% performance improvement  
• Mentored 2 junior developers and led code review sessions
• Collaborated with cross-functional teams using Agile methodologies

Junior Python Developer - StartupXYZ (2020-2021)
• Developed backend services using Django and PostgreSQL
• Implemented REST API endpoints for frontend React applications
• Participated in technical discussions and system design reviews

EDUCATION:
Bachelor of Computer Science - Tech University (2020)

KEY PROJECTS:
• E-commerce Backend: Django-based REST API with PostgreSQL, deployed on AWS
• Scalable Task Management System: Python backend serving React frontend',
    0.89,
    'Optimized for Senior Python Developer role at Innovation Labs. Key changes:
- Emphasized Python and Django experience in summary
- Highlighted REST API development and scalability achievements
- Added mentoring experience relevant to senior role requirements
- Restructured technical skills to prioritize Python ecosystem
- Quantified achievements (10,000+ users, 40% improvement)
- Aligned project descriptions with job requirements
- Enhanced backend development focus while maintaining full-stack capability',
    CURRENT_TIMESTAMP
);

-- Sample application
INSERT INTO careeragent.applications (
    id,
    job_posting_id,
    resume_id,
    cover_letter,
    status,
    submitted_at,
    notes
) VALUES (
    'sample-application-1',
    'sample-job-1',
    'sample-resume-1',
    'Dear Innovation Labs Hiring Team,

I am writing to express my strong interest in the Senior Python Developer position at Innovation Labs. With over 3 years of hands-on experience building scalable backend services using Python and Django, I am excited about the opportunity to contribute to your dynamic team.

In my current role at Tech Corp, I have successfully designed and developed robust REST APIs that serve over 10,000 daily users, directly aligning with your requirements for building services that handle millions of requests. My experience with PostgreSQL optimization, where I achieved a 40% performance improvement, demonstrates my commitment to building efficient and scalable solutions.

What particularly excites me about this role is the opportunity to mentor junior developers, an aspect of my current position that I find incredibly rewarding. I have been actively involved in code reviews and have guided two junior team members in their professional growth, helping them develop best practices in Python development and system design.

Your emphasis on modern development practices and collaborative work environment resonates with my professional values. I am experienced in working with cross-functional teams and have consistently delivered high-quality code while maintaining excellent communication with designers and product managers.

I am particularly drawn to Innovation Labs'' commitment to innovation and would welcome the opportunity to discuss how my technical expertise in Python, Django, and scalable system design can contribute to your team''s continued success.

Thank you for considering my application. I look forward to hearing from you.

Best regards,
John Doe',
    'completed',
    CURRENT_TIMESTAMP,
    'Successfully submitted application via automated system. Form filling completed without errors.'
);

-- ================================================
-- 5. VERIFICATION QUERIES
-- ================================================

-- Verify schema creation
SELECT 'Schema created successfully' as status
WHERE EXISTS (
    SELECT 1 FROM information_schema.schemata 
    WHERE schema_name = 'careeragent'
);

-- List all tables created
SELECT 
    table_name,
    table_type
FROM information_schema.tables 
WHERE table_schema = 'careeragent'
ORDER BY table_name;

-- Count records in each table
SELECT 
    'resumes' as table_name, 
    COUNT(*) as record_count 
FROM careeragent.resumes
UNION ALL
SELECT 
    'job_postings' as table_name, 
    COUNT(*) as record_count 
FROM careeragent.job_postings
UNION ALL
SELECT 
    'applications' as table_name, 
    COUNT(*) as record_count 
FROM careeragent.applications
UNION ALL
SELECT 
    'optimized_resumes' as table_name, 
    COUNT(*) as record_count 
FROM careeragent.optimized_resumes
ORDER BY table_name;

-- Verify indexes created
SELECT 
    indexname,
    tablename
FROM pg_indexes 
WHERE schemaname = 'careeragent'
ORDER BY tablename, indexname;

-- Final success message
SELECT 
    '🎉 AI Career Agent database setup completed successfully!' as status,
    'Ready to run: python cli.py report' as next_step;