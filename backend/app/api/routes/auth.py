from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from backend.app.db.session import get_db
from backend.app.db.models import Profile, PasswordResetToken
from backend.app.core.config import settings
from backend.app.core.security import (
    verify_password, get_password_hash, create_access_token, decode_access_token,
    validate_password_strength, generate_secure_reset_token, hash_token
)
from backend.app.core.deps import get_current_user
from backend.app.core.rate_limit import rate_limiter
from backend.app.services.email import email_service

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
def register(req: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    # Rate limit registration attempts per IP
    client_ip = request.client.host if request.client else "unknown"
    rate_limiter.enforce(f"register_{client_ip}", max_requests=settings.RATE_LIMIT_AUTH_PER_MINUTE, window_seconds=60, action_name="Registration")

    # Enforce production password policy
    try:
        validate_password_strength(req.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    clean_email = req.email.lower().strip()
    existing = db.query(Profile).filter(Profile.email == clean_email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )
    
    hashed = get_password_hash(req.password)
    user = Profile(
        email=clean_email,
        hashed_password=hashed,
        display_name=req.display_name or clean_email.split("@")[0],
        token_version=1
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": user.id, "email": user.email, "tv": user.token_version})
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
def login(req: LoginRequest, request: Request, db: Session = Depends(get_db)):
    clean_email = req.email.lower().strip()
    client_ip = request.client.host if request.client else "unknown"
    rate_limiter.enforce(f"login_{clean_email}_{client_ip}", max_requests=15, window_seconds=60, action_name="Login")

    user = db.query(Profile).filter(Profile.email == clean_email).first()
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

    # Issue token containing active token_version
    tv = getattr(user, "token_version", 1) or 1
    token = create_access_token(data={"sub": user.id, "email": user.email, "tv": tv})
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
def forgot_password(req: ForgotPasswordRequest, request: Request, db: Session = Depends(get_db)):
    """
    Secure password reset request endpoint.
    - NEVER returns reset token in response.
    - Returns identical generic response for registered and unregistered emails (defends against enumeration).
    - Generates cryptographically secure single-use token and stores SHA-256 hash.
    - Dispatches reset link through the configured email service adapter.
    """
    clean_email = req.email.lower().strip()
    client_ip = request.client.host if request.client else "unknown"
    rate_limiter.enforce(f"forgot_{clean_email}_{client_ip}", max_requests=5, window_seconds=900, action_name="Password reset")

    # Generic message returned unconditionally to prevent user enumeration
    GENERIC_RESPONSE = {
        "message": "If this email address is registered, password reset instructions have been sent."
    }

    user = db.query(Profile).filter(Profile.email == clean_email).first()
    if not user:
        return GENERIC_RESPONSE

    # Generate single-use token and compute SHA-256 hash
    raw_token, token_hash = generate_secure_reset_token()
    now = datetime.utcnow()
    expires_at = now + timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES)

    # Invalidate any previously active unused tokens for this user
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used_at.is_(None)
    ).update({"used_at": now})

    # Save new hashed token record
    reset_record = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
        created_at=now
    )
    db.add(reset_record)
    db.commit()

    # Dispatch email through adapter (never logs the raw token in application logs)
    email_service.send_password_reset_email(
        to_email=user.email,
        reset_token=raw_token,
        user_name=user.display_name
    )

    return GENERIC_RESPONSE

@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Atomic password reset confirmation endpoint.
    - Validates token hash and expiration.
    - Validates new password strength.
    - Marks token used atomically to prevent replay or race-condition consumption.
    - Increments user token_version to invalidate all pre-existing sessions.
    """
    if not req.reset_token or not req.reset_token.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token is required."
        )

    # Enforce password policy
    try:
        validate_password_strength(req.new_password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    token_hash = hash_token(req.reset_token)
    now = datetime.utcnow()

    # Query token atomically
    token_record = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == token_hash,
        PasswordResetToken.used_at.is_(None)
    ).with_for_update().first()

    if not token_record or token_record.expires_at < now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token."
        )

    # Mark token used immediately to prevent replay
    token_record.used_at = now

    user = db.query(Profile).filter(Profile.id == token_record.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User account not found.")

    # Update password and increment token_version to invalidate all existing sessions
    user.hashed_password = get_password_hash(req.new_password)
    user.token_version = (getattr(user, "token_version", 1) or 1) + 1

    # Invalidate any other outstanding tokens
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used_at.is_(None)
    ).update({"used_at": now})

    db.commit()
    return {"message": "Password has been reset successfully. All previous sessions have been invalidated. Please log in with your new credentials."}

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
def logout(current_user: Profile = Depends(get_current_user), db: Session = Depends(get_db)):
    """Server-side session invalidation by incrementing token_version."""
    current_user.token_version = (getattr(current_user, "token_version", 1) or 1) + 1
    db.commit()
    return {"message": "Successfully logged out. Active sessions have been invalidated."}
