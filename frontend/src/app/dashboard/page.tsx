'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowLeftIcon, ChartBarIcon, BriefcaseIcon, DocumentTextIcon, CheckCircleIcon } from '@heroicons/react/24/outline'

interface DashboardStats {
  totalJobs: number
  totalResumes: number
  totalApplications: number
  successRate: number
  applicationsByStatus: Record<string, number>
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats>({
    totalJobs: 0,
    totalResumes: 0,
    totalApplications: 0,
    successRate: 0,
    applicationsByStatus: {}
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const [jobsResponse, resumesResponse, applicationsResponse] = await Promise.all([
        fetch('/api/jobs'),
        fetch('/api/resumes'),
        fetch('/api/applications')
      ])

      const [jobs, resumes, applications] = await Promise.all([
        jobsResponse.json(),
        resumesResponse.json(),
        applicationsResponse.json()
      ])

      const applicationsByStatus = applications.reduce((acc: Record<string, number>, app: any) => {
        acc[app.status] = (acc[app.status] || 0) + 1
        return acc
      }, {})

      const completedApps = applicationsByStatus.COMPLETED || 0
      const successRate = applications.length > 0 ? (completedApps / applications.length) * 100 : 0

      setStats({
        totalJobs: jobs.length,
        totalResumes: resumes.length,
        totalApplications: applications.length,
        successRate,
        applicationsByStatus
      })
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
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
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-2">Overview of your job application progress and analytics</p>
        </div>

        {/* Stats Cards */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">Total Jobs</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalJobs}</p>
              </div>
              <BriefcaseIcon className="h-8 w-8 text-blue-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">Resumes</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalResumes}</p>
              </div>
              <DocumentTextIcon className="h-8 w-8 text-green-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">Applications</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalApplications}</p>
              </div>
              <ChartBarIcon className="h-8 w-8 text-purple-600" />
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">Success Rate</p>
                <p className="text-2xl font-bold text-gray-900">{stats.successRate.toFixed(1)}%</p>
              </div>
              <CheckCircleIcon className="h-8 w-8 text-yellow-600" />
            </div>
          </div>
        </div>

        {/* Application Status Breakdown */}
        <div className="grid md:grid-cols-2 gap-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Application Status</h3>
            {Object.keys(stats.applicationsByStatus).length === 0 ? (
              <p className="text-gray-500">No applications yet</p>
            ) : (
              <div className="space-y-3">
                {Object.entries(stats.applicationsByStatus).map(([status, count]) => (
                  <div key={status} className="flex justify-between items-center">
                    <span className="text-gray-700 capitalize">{status.toLowerCase()}</span>
                    <span className="font-medium text-gray-900">{count}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
            <div className="space-y-4">
              <div className="flex items-center text-sm">
                <div className="w-2 h-2 bg-blue-600 rounded-full mr-3"></div>
                <span className="text-gray-600">System initialized and ready</span>
              </div>
              <div className="flex items-center text-sm">
                <div className="w-2 h-2 bg-green-600 rounded-full mr-3"></div>
                <span className="text-gray-600">Job discovery agent standing by</span>
              </div>
              <div className="flex items-center text-sm">
                <div className="w-2 h-2 bg-purple-600 rounded-full mr-3"></div>
                <span className="text-gray-600">Resume parser ready for uploads</span>
              </div>
            </div>
          </div>
        </div>

        {/* System Status */}
        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Agent Status</h3>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
              <span className="text-blue-900">Job Discovery Agent</span>
              <span className="px-2 py-1 bg-blue-200 text-blue-800 rounded text-xs">Ready</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
              <span className="text-green-900">Resume Parser Agent</span>
              <span className="px-2 py-1 bg-green-200 text-green-800 rounded text-xs">Ready</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
              <span className="text-yellow-900">Application Agent</span>
              <span className="px-2 py-1 bg-yellow-200 text-yellow-800 rounded text-xs">Pending</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}