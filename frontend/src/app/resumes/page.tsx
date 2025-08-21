'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeftIcon, DocumentTextIcon, PlusIcon } from '@heroicons/react/24/outline'

interface Resume {
  id: string
  filePath: string
  skills: string[]
  experienceYears: number
  createdAt: string
  updatedAt: string
  _count: {
    applications: number
  }
}

export default function ResumesPage() {
  const [resumes, setResumes] = useState<Resume[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)

  useEffect(() => {
    fetchResumes()
  }, [])

  const fetchResumes = async () => {
    try {
      const response = await fetch('/api/resumes')
      const data = await response.json()
      setResumes(data)
    } catch (error) {
      console.error('Error fetching resumes:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setUploading(true)
    try {
      // In a real implementation, you would:
      // 1. Upload the file to storage
      // 2. Extract text content using the resume parser agent
      // 3. Save to database
      
      const mockResume = {
        filePath: file.name,
        content: 'Parsed resume content would go here',
        skills: ['JavaScript', 'React', 'Node.js'], // Would be extracted by AI
        experienceYears: 3, // Would be calculated by AI
        education: [],
        workHistory: []
      }

      const response = await fetch('/api/resumes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(mockResume)
      })

      if (response.ok) {
        fetchResumes() // Refresh the list
      }
    } catch (error) {
      console.error('Error uploading resume:', error)
    } finally {
      setUploading(false)
    }
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
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Resume Management</h1>
              <p className="text-gray-600 mt-2">Upload and manage your resumes with AI-powered analysis</p>
            </div>
            <label className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 cursor-pointer inline-flex items-center">
              <PlusIcon className="h-4 w-4 mr-2" />
              Upload Resume
              <input
                type="file"
                accept=".pdf,.doc,.docx"
                onChange={handleFileUpload}
                className="hidden"
                disabled={uploading}
              />
            </label>
          </div>
        </div>

        {uploading && (
          <div className="bg-blue-50 border border-blue-200 rounded-md p-4 mb-6">
            <p className="text-blue-700">Uploading and processing resume...</p>
          </div>
        )}

        <div className="grid gap-6">
          {resumes.length === 0 ? (
            <div className="text-center py-12">
              <DocumentTextIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500 mb-4">No resumes uploaded yet.</p>
              <label className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 cursor-pointer inline-flex items-center">
                <PlusIcon className="h-4 w-4 mr-2" />
                Upload Your First Resume
                <input
                  type="file"
                  accept=".pdf,.doc,.docx"
                  onChange={handleFileUpload}
                  className="hidden"
                  disabled={uploading}
                />
              </label>
            </div>
          ) : (
            resumes.map((resume) => (
              <div key={resume.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex items-center">
                    <DocumentTextIcon className="h-8 w-8 text-gray-400 mr-3" />
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{resume.filePath}</h3>
                      <p className="text-gray-600 text-sm">
                        {resume.experienceYears} years experience
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
                      {resume._count.applications} application{resume._count.applications !== 1 ? 's' : ''}
                    </span>
                  </div>
                </div>

                {resume.skills.length > 0 && (
                  <div className="mb-4">
                    <h4 className="font-medium text-gray-900 mb-2">Skills:</h4>
                    <div className="flex flex-wrap gap-2">
                      {resume.skills.map((skill, index) => (
                        <span key={index} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex justify-between items-center text-sm text-gray-500">
                  <span>Uploaded: {new Date(resume.createdAt).toLocaleDateString()}</span>
                  <span>Last updated: {new Date(resume.updatedAt).toLocaleDateString()}</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}