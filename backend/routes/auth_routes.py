from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserCreate, UserLogin, UserResponse, Token
from utils import hash_password, verify_password, create_access_token,get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from models import User
from schemas import UserLogin
from datetime import timedelta
from slowapi import Limiter
from slowapi.util import get_remote_address
import jwt
import os


SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"

router = APIRouter(prefix="/auth", tags=["Authentication"])
limiter = Limiter(key_func=get_remote_address)

# User Registration Route
@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)
    new_user = User(name=user.name, email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  

    return new_user


@router.post("/login")
def login(user_data: UserLogin, response: Response, db: Session = Depends(get_db)):
    """
    Login a user and set JWT in httpOnly cookie.
    """
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.email, "role": user.role}, expires_delta=timedelta(hours=1))
    
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True, 
        secure=False,  
        samesite="Lax"
    )

    return {"message": "Login successful", "role": user.role, "user_id": user.id, "token":access_token}


@router.post("/refresh")
def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):

    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        token = token.replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

    
        new_access_token = create_access_token(data={"sub": user.email, "role": user.role}, expires_delta=timedelta(hours=1))

        response.set_cookie(
            key="access_token",
            value=f"Bearer {new_access_token}",
            httponly=True,
            secure=False, 
            samesite="Lax"
        )

        return {"message": "Token refreshed successfully"}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired. Please log in again.")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/me", response_model=UserResponse)
def get_current_user_info(request: Request, current_user: User = Depends(get_current_user)):
 
    token = request.cookies.get("access_token")
    print(token)

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return current_user
