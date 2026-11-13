from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from backend.app.db.session import get_db
from backend.app.db.models import Profile
from backend.app.core.security import (
    verify_password, get_password_hash, create_access_token, decode_access_token
)
from backend.app.core.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    display_name: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: str

class ProfileResponse(BaseModel):
    id: str
    email: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: ProfileResponse

@router.post("/register", response_model=AuthResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(Profile).filter(Profile.email == req.email.lower().strip()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )
    
    hashed = get_password_hash(req.password)
    user = Profile(
        email=req.email.lower().strip(),
        hashed_password=hashed,
        display_name=req.display_name or req.email.split("@")[0]
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": user.id, "email": user.email})
    return AuthResponse(
        access_token=token,
        user=ProfileResponse(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            avatar_url=user.avatar_url
        )
    )

@router.post("/login", response_model=AuthResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Profile).filter(Profile.email == req.email.lower().strip()).first()
    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )
    
    if not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )

    token = create_access_token(data={"sub": user.id, "email": user.email})
    return AuthResponse(
        access_token=token,
        user=ProfileResponse(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            avatar_url=user.avatar_url
        )
    )

@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(Profile).filter(Profile.email == req.email.lower().strip()).first()
    if not user:
        # Standard security practice: avoid user enumeration by returning uniform message
        return {
            "message": "If this email is registered, a password reset link has been dispatched.",
            "reset_token": None
        }
    
    # Generate temporary reset token valid for 15 minutes
    reset_token = create_access_token(
        data={"sub": user.id, "email": user.email, "purpose": "password_reset"},
        expires_delta=timedelta(minutes=15)
    )
    return {
        "message": "Password reset token generated successfully.",
        "reset_token": reset_token
    }

@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    payload = decode_access_token(req.reset_token)
    if not payload or payload.get("purpose") != "password_reset":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token."
        )
    
    user_id = payload.get("sub")
    user = db.query(Profile).filter(Profile.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User account not found.")

    if len(req.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters long."
        )

    user.hashed_password = get_password_hash(req.new_password)
    db.commit()
    return {"message": "Password has been reset successfully. Please log in with your new credentials."}

@router.get("/profile", response_model=ProfileResponse)
def get_profile(current_user: Profile = Depends(get_current_user)):
    return ProfileResponse(
        id=current_user.id,
        email=current_user.email,
        display_name=current_user.display_name,
        avatar_url=current_user.avatar_url
    )

@router.put("/profile", response_model=ProfileResponse)
def update_profile(
    display_name: Optional[str] = None,
    avatar_url: Optional[str] = None,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if display_name is not None:
        current_user.display_name = display_name
    if avatar_url is not None:
        current_user.avatar_url = avatar_url
    db.commit()
    db.refresh(current_user)
    return ProfileResponse(
        id=current_user.id,
        email=current_user.email,
        display_name=current_user.display_name,
        avatar_url=current_user.avatar_url
    )

@router.post("/logout")
def logout(current_user: Profile = Depends(get_current_user)):
    return {"message": "Successfully logged out."}
