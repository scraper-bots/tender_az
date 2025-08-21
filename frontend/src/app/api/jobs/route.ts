import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const status = searchParams.get('status')
    
    const jobs = await prisma.jobPosting.findMany({
      where: status ? { status: status as any } : undefined,
      orderBy: { discoveredAt: 'desc' },
      include: {
        applications: true,
        _count: {
          select: { applications: true }
        }
      }
    })

    return NextResponse.json(jobs)
  } catch (error) {
    console.error('Error fetching jobs:', error)
    return NextResponse.json({ error: 'Failed to fetch jobs' }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    const job = await prisma.jobPosting.create({
      data: {
        title: body.title,
        company: body.company,
        location: body.location,
        description: body.description,
        requirements: body.requirements || [],
        salaryRange: body.salaryRange,
        url: body.url,
        status: body.status || 'DISCOVERED'
      }
    })

    return NextResponse.json(job)
  } catch (error) {
    console.error('Error creating job:', error)
    return NextResponse.json({ error: 'Failed to create job' }, { status: 500 })
  }
}