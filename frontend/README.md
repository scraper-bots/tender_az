# AI Career Agent Frontend

Next.js frontend for the AI Career Agent system with Vercel deployment support.

## Features

- **Job Discovery Dashboard** - View and filter discovered job opportunities
- **Resume Management** - Upload and manage resumes with AI analysis
- **Application Tracking** - Monitor application status and success rates
- **Analytics Dashboard** - Track performance metrics and system health

## Tech Stack

- **Framework**: Next.js 15 with App Router
- **Styling**: Tailwind CSS 4
- **Database**: PostgreSQL with Prisma ORM
- **Deployment**: Vercel
- **UI Components**: Headless UI, Heroicons

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your database credentials and API keys
   ```

3. **Database setup:**
   ```bash
   npm run db:generate  # Generate Prisma client
   npm run db:push     # Push schema to database
   ```

4. **Run development server:**
   ```bash
   npm run dev
   ```

## Database Configuration

The app uses PostgreSQL with the `careeragent` schema. Configure your `DATABASE_URL` in the environment variables:

```
DATABASE_URL="postgresql://username:password@hostname:port/database"
```

## Deployment to Vercel

1. **Connect to Vercel:**
   - Import the project in Vercel dashboard
   - Connect your Git repository

2. **Configure environment variables in Vercel:**
   - `DATABASE_URL`
   - `OPENAI_API_KEY` 
   - `ANTHROPIC_API_KEY`

3. **Deploy:**
   ```bash
   vercel deploy
   ```

The `vercel.json` configuration handles the build process and environment setup.

## API Routes

- `GET /api/jobs` - List job postings
- `POST /api/jobs` - Create job posting
- `GET /api/resumes` - List resumes
- `POST /api/resumes` - Upload resume
- `GET /api/applications` - List applications
- `POST /api/applications` - Create application
