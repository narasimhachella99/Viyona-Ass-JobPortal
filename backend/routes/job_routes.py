from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from models import Job, User
from schemas import JobCreate, JobResponse
from utils import get_current_user
from typing import List
import json
from database import get_db, redis_client

router = APIRouter(prefix="/jobs", tags=["Jobs"])

import json
from fastapi import HTTPException, Request, Depends
from sqlalchemy.orm import Session
from typing import List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[JobResponse])
def get_jobs(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated. Please log in.")

        cache_key = "all_jobs_list"

        if redis_client:
            cached_jobs = redis_client.get(cache_key)
            if cached_jobs:
                return json.loads(cached_jobs)

        jobs = db.query(Job).all()

    
        job_list = [job.__dict__ for job in jobs]
        for job in job_list:
            job.pop("_sa_instance_state", None) 

        if redis_client:
            redis_client.setex(cache_key, 300, json.dumps(job_list))

        return job_list

    except Exception as e:
        logger.error(f"An error occurred while retrieving jobs: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")



@router.post("/", response_model=JobResponse)
def create_job(
    request: Request,
    job: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  
):
   
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized. Only admins can create jobs.")

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

@router.get("/paginated", response_model=List[JobResponse])
def get_jobs_paginated(
    db: Session = Depends(get_db),
    skip: int = Query(0, alias="page", description="Page number (starts from 0)"),
    limit: int = Query(10, alias="size", description="Number of results per page")
):
    
    jobs = db.query(Job).offset(skip * limit).limit(limit).all()
    return jobs


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    request: Request,
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  
):
   
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated. Please log in.")

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
