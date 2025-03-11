from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from database import get_db
from models import Application, Job, User
from schemas import ApplicationCreate, ApplicationResponse, UpdateStatusRequest
from utils import get_current_user
from typing import List, Dict
from datetime import datetime

router = APIRouter(prefix="/applications", tags=["Applications"])

@router.post("/", response_model=ApplicationResponse)
def apply_for_job(
    request: Request,
    application: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  
):
   
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated. Please log in.")

    job = db.query(Job).filter(Job.id == application.job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    existing_application = db.query(Application).filter(
        Application.job_id == application.job_id,
        Application.user_id == current_user.id
    ).first()
    if existing_application:
        raise HTTPException(status_code=400, detail="You have already applied for this job.")

    new_application = Application(
        job_id=application.job_id,
        user_id=current_user.id, 
        status="Pending",
        applied_at=datetime.utcnow()
    )
    
    db.add(new_application)
    db.commit()
    db.refresh(new_application)

    return new_application

@router.get("/my-applications", response_model=List[ApplicationResponse])
def get_user_applications(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  
):
  
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated. Please log in.")

    applications = db.query(Application).filter(Application.user_id == current_user.id).all()
    return applications 

@router.get("/all", response_model=List[ApplicationResponse])
def get_all_job_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
   
    if not current_user or current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized. Admins only.")

    applications = db.query(Application).all()
    return applications


@router.get("/{job_id}", response_model=List[ApplicationResponse])
def get_job_applicants(
    job_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
   
    if not current_user or current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized. Admins only.")

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    applicants = db.query(Application).filter(Application.job_id == job_id).all()
    if not applicants:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No applicants found for this job")

    return applicants



@router.put("/{app_id}")
def update_application_status(
    app_id: int, 
    request: UpdateStatusRequest,  
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  
) -> Dict[str, str]:
   
    if not current_user or current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized. Admins only.")

    application = db.query(Application).filter(Application.id == app_id).first()
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    if request.new_status not in ["Pending", "Approved", "Rejected"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")

    application.status = request.new_status
    db.commit()
    db.refresh(application)

    return {"message": "Application status updated successfully"}


