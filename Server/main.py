from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, SessionLocal
from routes.auth_routes import router as auth_router
from routes.job_routes import router as job_router
from routes.application_routes import router as application_router
from models import Base, User
from utils import hash_password
from sqlalchemy.orm import Session

app = FastAPI(
    title="Job Board API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(job_router, prefix="/jobs", tags=["Jobs"])
app.include_router(application_router, prefix="/applications", tags=["Applications"])

def create_default_admin():
    db: Session = SessionLocal()
    admin_email = "admin@jobbord.com"
    existing_admin = db.query(User).filter(User.email == admin_email).first()

    if not existing_admin:
        admin_user = User(
            name="Admin User",
            email=admin_email,
            password=hash_password("Admin@123"),  
            role="admin"
        )
        db.add(admin_user)
        db.commit()
        print("Default admin account created!")
    db.close()

create_default_admin()

@app.get("/", tags=["Root"])
def root():
    return {"message": "Welcome to the Job Board API! Visit /docs for API documentation."}
