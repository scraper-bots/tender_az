import Link from 'next/link'
import { BriefcaseIcon, DocumentTextIcon, ChartBarIcon } from '@heroicons/react/24/outline'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            AI Career Agent
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Intelligent job application automation with multi-agent coordination.
            Let AI find, optimize, and apply for jobs on your behalf.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <Link href="/jobs" className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
            <BriefcaseIcon className="h-12 w-12 text-blue-600 mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Job Discovery</h3>
            <p className="text-gray-600">Browse discovered job opportunities and track application status.</p>
          </Link>

          <Link href="/resumes" className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
            <DocumentTextIcon className="h-12 w-12 text-green-600 mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Resume Management</h3>
            <p className="text-gray-600">Upload and manage your resumes with AI-powered optimization.</p>
          </Link>

          <Link href="/dashboard" className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
            <ChartBarIcon className="h-12 w-12 text-purple-600 mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Analytics</h3>
            <p className="text-gray-600">Track application success rates and optimize your strategy.</p>
          </Link>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">How It Works</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold text-lg mb-2">1. Upload Resume</h3>
              <p className="text-gray-600 mb-4">Upload your resume and let our AI parse and analyze your skills and experience.</p>
              
              <h3 className="font-semibold text-lg mb-2">2. Job Discovery</h3>
              <p className="text-gray-600">Our agents automatically discover and analyze job opportunities from various sources.</p>
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-2">3. Resume Optimization</h3>
              <p className="text-gray-600 mb-4">AI optimizes your resume for each specific job application to maximize match scores.</p>
              
              <h3 className="font-semibold text-lg mb-2">4. Auto Application</h3>
              <p className="text-gray-600">Intelligent agents submit applications with tailored resumes and cover letters.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
