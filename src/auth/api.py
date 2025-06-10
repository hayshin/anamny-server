from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from .schemas import (
    UserCreate, UserResponse, LoginRequest, Token,
    PasswordResetRequest, PasswordResetConfirm, UserUpdate
)
from .crud import (
    create_user, authenticate_user, create_password_reset_token,
    reset_password, update_user_profile
)
from .utils import create_access_token
from .dependencies import get_current_active_user
from .models import User
from ..config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    try:
        db_user = create_user(db=db, user=user)
        return db_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
def login_user(user_credentials: LoginRequest, db: Session = Depends(get_db)):
    """Login user and return JWT token."""
    user = authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/forgot-password")
def forgot_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    """Request password reset."""
    reset_token = create_password_reset_token(db=db, email=request.email)
    if not reset_token:
        # Don't reveal if email exists or not for security
        return {"message": "If the email exists, a password reset link has been sent"}
    
    # TODO: Send email with reset link
    # For now, we'll just return success (in production, send email)
    print(f"Password reset token for {request.email}: {reset_token.token}")
    
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password")
def reset_user_password(request: PasswordResetConfirm, db: Session = Depends(get_db)):
    """Reset password using reset token."""
    success = reset_password(db=db, token=request.token, new_password=request.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    return {"message": "Password successfully reset"}


@router.get("/profile", response_model=UserResponse)
def get_user_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user profile."""
    return current_user


@router.patch("/profile", response_model=UserResponse)
def update_user_profile_endpoint(
    profile_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user profile."""
    updated_user = update_user_profile(db=db, user_id=current_user.id, user_update=profile_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated_user
