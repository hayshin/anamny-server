from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from .models import User, PasswordResetToken
from .schemas import UserCreate, UserUpdate
from .utils import get_password_hash, generate_reset_token, create_reset_token_expires


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username."""
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user."""
    # Check if user already exists
    if get_user_by_email(db, user.email):
        raise ValueError("Email already registered")
    if get_user_by_username(db, user.username):
        raise ValueError("Username already taken")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_profile(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """Update user profile."""
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password."""
    from .utils import verify_password
    
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_password_reset_token(db: Session, email: str) -> Optional[PasswordResetToken]:
    """Create a password reset token."""
    user = get_user_by_email(db, email)
    if not user:
        return None
    
    # Invalidate any existing tokens for this email
    db.query(PasswordResetToken).filter(
        and_(PasswordResetToken.email == email, PasswordResetToken.used == False)
    ).update({"used": True})
    
    token = generate_reset_token()
    db_token = PasswordResetToken(
        email=email,
        token=token,
        expires_at=create_reset_token_expires()
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token


def verify_reset_token(db: Session, token: str) -> Optional[PasswordResetToken]:
    """Verify a password reset token."""
    db_token = db.query(PasswordResetToken).filter(
        and_(
            PasswordResetToken.token == token,
            PasswordResetToken.used == False,
            PasswordResetToken.expires_at > datetime.utcnow()
        )
    ).first()
    return db_token


def reset_password(db: Session, token: str, new_password: str) -> bool:
    """Reset user password using reset token."""
    db_token = verify_reset_token(db, token)
    if not db_token:
        return False
    
    user = get_user_by_email(db, db_token.email)
    if not user:
        return False
    
    # Update password
    user.hashed_password = get_password_hash(new_password)
    
    # Mark token as used
    db_token.used = True
    
    db.commit()
    return True
