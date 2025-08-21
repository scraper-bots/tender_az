import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const status = searchParams.get('status')
    
    const applications = await prisma.application.findMany({
      where: status ? { status: status as any } : undefined,
      orderBy: { submittedAt: 'desc' },
      include: {
        jobPosting: true,
        resume: true
      }
    })

    return NextResponse.json(applications)
  } catch (error) {
    console.error('Error fetching applications:', error)
    return NextResponse.json({ error: 'Failed to fetch applications' }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    const application = await prisma.application.create({
      data: {
        jobPostingId: body.jobPostingId,
        resumeId: body.resumeId,
        coverLetter: body.coverLetter,
        status: body.status || 'PENDING',
        notes: body.notes
      },
      include: {
        jobPosting: true,
        resume: true
      }
    })

    return NextResponse.json(application)
  } catch (error) {
    console.error('Error creating application:', error)
    return NextResponse.json({ error: 'Failed to create application' }, { status: 500 })
  }
}