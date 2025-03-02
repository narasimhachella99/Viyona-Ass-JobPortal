from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Application, Job, User
from schemas import ApplicationCreate, ApplicationResponse, JobResponse
from utils import get_current_user
from typing import List
from datetime import datetime
from typing import Dict

router = APIRouter(prefix="/applications", tags=["Applications"])

@router.post("/", response_model=ApplicationResponse)
def apply_for_job(application: ApplicationCreate, db: Session = Depends(get_db)):
   
    job = db.query(Job).filter(Job.id == application.job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

  
    new_application = Application(
        job_id=application.job_id,
        user_id=application.user_id,  
        status="Pending",
        applied_at=datetime.utcnow()
    )
    
    db.add(new_application)
    db.commit()
    db.refresh(new_application)

    return new_application


@router.get("/my-applications", response_model=list[ApplicationResponse])
def get_user_applications(user_id: int, db: Session = Depends(get_db)):
    
    try:
        applications = db.query(Application).filter(Application.user_id == user_id).all()
        return applications
    except Exception as e:
        return {"error": str(e)}


class Config:
    from_attributes = True
ApplicationResponse.Config = Config
JobResponse.Config = Config


@router.get("/", response_model=List[ApplicationResponse])
def get_user_applications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    applications = db.query(Application).filter(Application.user_id == current_user.id).all()
    return applications

# Get Applications for a Specific Job
@router.get("/{job_id}", response_model=List[ApplicationResponse])
def get_job_applicants(job_id: int, db: Session = Depends(get_db)):
   
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    applicants = db.query(Application).filter(Application.job_id == job_id).all()

    if not applicants:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No applicants found for this job")

    return applicants

@router.put("/{app_id}", )
def update_application_status(
    app_id: int, new_status: str, db: Session = Depends(get_db)  
) -> Dict[str, str]:
   
    application = db.query(Application).filter(Application.id == app_id).first()
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")


    if new_status not in ["Pending", "Approved", "Rejected"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")

    application.status = new_status
    db.commit()

    return {"message": "Application status updated successfully"}