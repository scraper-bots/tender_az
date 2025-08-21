import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'

export async function GET() {
  try {
    const resumes = await prisma.resume.findMany({
      orderBy: { createdAt: 'desc' },
      include: {
        applications: {
          include: {
            jobPosting: true
          }
        },
        _count: {
          select: { applications: true }
        }
      }
    })

    return NextResponse.json(resumes)
  } catch (error) {
    console.error('Error fetching resumes:', error)
    return NextResponse.json({ error: 'Failed to fetch resumes' }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    const resume = await prisma.resume.create({
      data: {
        filePath: body.filePath,
        content: body.content,
        skills: body.skills || [],
        experienceYears: body.experienceYears || 0,
        education: body.education || [],
        workHistory: body.workHistory || []
      }
    })

    return NextResponse.json(resume)
  } catch (error) {
    console.error('Error creating resume:', error)
    return NextResponse.json({ error: 'Failed to create resume' }, { status: 500 })
  }
}