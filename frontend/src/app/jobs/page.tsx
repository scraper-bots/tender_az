'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeftIcon } from '@heroicons/react/24/outline'

interface JobPosting {
  id: string
  title: string
  company: string
  location: string
  description: string
  requirements: string[]
  salaryRange?: string
  url: string
  discoveredAt: string
  status: 'DISCOVERED' | 'APPLIED' | 'REJECTED' | 'INTERVIEW' | 'OFFER'
  _count: {
    applications: number
  }
}

export default function JobsPage() {
  const [jobs, setJobs] = useState<JobPosting[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<string>('all')

  useEffect(() => {
    fetchJobs()
  }, [filter])

  const fetchJobs = async () => {
    try {
      const url = filter === 'all' ? '/api/jobs' : `/api/jobs?status=${filter}`
      const response = await fetch(url)
      const data = await response.json()
      setJobs(data)
    } catch (error) {
      console.error('Error fetching jobs:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status: string) => {
    const colors = {
      DISCOVERED: 'bg-blue-100 text-blue-800',
      APPLIED: 'bg-yellow-100 text-yellow-800',
      REJECTED: 'bg-red-100 text-red-800',
      INTERVIEW: 'bg-green-100 text-green-800',
      OFFER: 'bg-purple-100 text-purple-800'
    }
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'
  }

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-6">
          <Link href="/" className="inline-flex items-center text-blue-600 hover:text-blue-800 mb-4">
            <ArrowLeftIcon className="h-4 w-4 mr-2" />
            Back to Home
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Job Opportunities</h1>
          <p className="text-gray-600 mt-2">Discovered job opportunities and their application status</p>
        </div>

        <div className="mb-6">
          <div className="flex space-x-2">
            {['all', 'DISCOVERED', 'APPLIED', 'INTERVIEW', 'OFFER'].map((status) => (
              <button
                key={status}
                onClick={() => setFilter(status)}
                className={`px-4 py-2 rounded-md text-sm font-medium ${
                  filter === status
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                } border border-gray-300`}
              >
                {status === 'all' ? 'All Jobs' : status.charAt(0) + status.slice(1).toLowerCase()}
              </button>
            ))}
          </div>
        </div>

        <div className="grid gap-6">
          {jobs.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500">No jobs found. The job discovery agent will populate this list automatically.</p>
            </div>
          ) : (
            jobs.map((job) => (
              <div key={job.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900">{job.title}</h3>
                    <p className="text-gray-600">{job.company} • {job.location}</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadge(job.status)}`}>
                      {job.status}
                    </span>
                    {job._count.applications > 0 && (
                      <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
                        {job._count.applications} application{job._count.applications > 1 ? 's' : ''}
                      </span>
                    )}
                  </div>
                </div>
                
                <p className="text-gray-700 mb-4 line-clamp-3">{job.description}</p>
                
                {job.requirements.length > 0 && (
                  <div className="mb-4">
                    <h4 className="font-medium text-gray-900 mb-2">Requirements:</h4>
                    <div className="flex flex-wrap gap-2">
                      {job.requirements.slice(0, 5).map((req, index) => (
                        <span key={index} className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-sm">
                          {req}
                        </span>
                      ))}
                      {job.requirements.length > 5 && (
                        <span className="text-gray-500 text-sm">+{job.requirements.length - 5} more</span>
                      )}
                    </div>
                  </div>
                )}
                
                <div className="flex justify-between items-center">
                  <div className="text-sm text-gray-500">
                    Discovered: {new Date(job.discoveredAt).toLocaleDateString()}
                    {job.salaryRange && <span className="ml-4">Salary: {job.salaryRange}</span>}
                  </div>
                  <a
                    href={job.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                  >
                    View Original →
                  </a>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}