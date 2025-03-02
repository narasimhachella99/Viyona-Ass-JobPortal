from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Job, User
from schemas import JobCreate, JobResponse
from utils import get_current_user
from typing import List


router = APIRouter(prefix="/jobs", tags=["Jobs"])

# Create a new job (Admin only)
@router.post("/", response_model=JobResponse)
def create_job(
    job: JobCreate,
    db: Session = Depends(get_db)
):
   
    try:
        if not job.title or not job.description or not job.company or not job.location:
            raise HTTPException(status_code=400, detail="All fields are required")
        
        new_job = Job(
            title=job.title.strip(),
            description=job.description.strip(),
            company=job.company.strip(),
            location=job.location.strip()
        )
        db.add(new_job)
        db.commit()
        db.refresh(new_job)

        return new_job
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/", response_model=List[JobResponse])
def get_jobs(
    db: Session = Depends(get_db),
    skip: int = Query(0, alias="page", description="Page number"),
    limit: int = Query(10, alias="size", description="Number of results per page")
):
   
    jobs = db.query(Job).offset(skip * limit).limit(limit).all()
    return jobs


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    updated_job: JobCreate,
    db: Session = Depends(get_db),
   
):

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    for key, value in updated_job.dict().items():
        if value:
            setattr(job, key, value.strip())
    
    db.commit()
    db.refresh(job)
    return job

@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    
  
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    db.delete(job)
    db.commit()
    return {"message": "Job deleted successfully"}
