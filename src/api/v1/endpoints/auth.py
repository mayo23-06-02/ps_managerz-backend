# src/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from typing import Optional
import secrets

from src.database.session import get_db
from src.models.user import User as DBUser
from src.models.auth import RefreshToken, PasswordResetToken
from src.schemas.auth import (
    TokenResponse,
    LoginRequest,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirmRequest,
    ChangePasswordRequest,
    UserProfileResponse
)
from src.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)
from src.api.dependencies import get_current_user

# Optional: Email service for password reset
# from src.services.email import send_password_reset_email

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate a user and return access and refresh tokens.
    
    - Requires username and password
    - Returns access token, refresh token, and expiration time
    - Raises 401 for invalid credentials
    """
    # Find the user by username
    user = db.query(DBUser).filter(DBUser.userName_str == form_data.username).first()
    
    # Check if user exists and password is correct
    if not user or not verify_password(form_data.password, user.password_str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if user.deleted_bol:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.userID)},
        expires_delta=access_token_expires
    )
    
    # Create refresh token
    refresh_token_value = create_refresh_token()
    refresh_token_expires = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    # Store refresh token in database
    db_refresh_token = RefreshToken(
        id=uuid4(),
        user_id=user.userID,
        token=refresh_token_value,
        expires_at=refresh_token_expires,
        created_at=datetime.utcnow(),
        revoked=False
    )
    
    try:
        db.add(db_refresh_token)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create refresh token"
        )
    
    # Return tokens
    return {
        "access_token": access_token,
        "refresh_token": refresh_token_value,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
    }

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh an access token using a valid refresh token.
    
    - Requires a valid refresh token
    - Returns new access token, refresh token, and expiration time
    - Revokes the old refresh token
    - Raises 401 for invalid or expired refresh tokens
    """
    # Find the refresh token
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == token_data.refresh_token,
        RefreshToken.revoked == False,
        RefreshToken.expires_at > datetime.utcnow()
    ).first()
    
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get the user
    user = db.query(DBUser).filter(DBUser.userID == db_token.user_id).first()
    if not user or user.deleted_bol:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Revoke the old refresh token
    db_token.revoked = True
    db_token.revoked_at = datetime.utcnow()
    
    # Create new access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.userID)},
        expires_delta=access_token_expires
    )
    
    # Create new refresh token
    new_refresh_token_value = create_refresh_token()
    refresh_token_expires = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    # Store new refresh token in database
    new_db_refresh_token = RefreshToken(
        id=uuid4(),
        user_id=user.userID,
        token=new_refresh_token_value,
        expires_at=refresh_token_expires,
        created_at=datetime.utcnow(),
        revoked=False
    )
    
    try:
        db.add(new_db_refresh_token)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create new refresh token"
        )
    
    # Return new tokens
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token_value,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
    }

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Logout a user by revoking their refresh token.
    
    - Requires the refresh token
    - Revokes the token in the database
    - Returns 204 No Content on success
    - Returns 404 if token not found
    """
    # Find and revoke the refresh token
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == token_data.refresh_token,
        RefreshToken.revoked == False
    ).first()
    
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found or already revoked"
        )
    
    # Revoke the token
    db_token.revoked = True
    db_token.revoked_at = datetime.utcnow()
    
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not revoke token"
        )
    
    return None  # 204 No Content

@router.post("/password-reset", status_code=status.HTTP_202_ACCEPTED)
async def request_password_reset(
    reset_request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Request a password reset for a user.
    
    - Requires the user's email
    - Creates a password reset token
    - Sends an email with reset instructions (in background)
    - Always returns 202 Accepted (even if email not found, for security)
    """
    # Find the user by email
    user = db.query(DBUser).filter(DBUser.email_str == reset_request.email).first()
    
    # If user exists and is active, create a reset token
    if user and not user.deleted_bol:
        # Generate token
        token_value = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        # Store token in database
        db_token = PasswordResetToken(
            id=uuid4(),
            user_id=user.userID,
            token=token_value,
            expires_at=expires_at,
            created_at=datetime.utcnow(),
            used=False
        )
        
        try:
            db.add(db_token)
            db.commit()
            
            # Send email in background
            # background_tasks.add_task(
            #     send_password_reset_email,
            #     email=user.email_str,
            #     token=token_value,
            #     username=user.userName_str
            # )
        except SQLAlchemyError:
            db.rollback()
            # Don't expose error details for security reasons
    
    # Always return 202 Accepted, even if user not found (security best practice)
    return {"message": "If the email exists in our system, a password reset link has been sent"}

@router.post("/password-reset/confirm", status_code=status.HTTP_200_OK)
async def confirm_password_reset(
    reset_data: PasswordResetConfirmRequest,
    db: Session = Depends(get_db)
):
    """
    Reset a user's password using a valid reset token.
    
    - Requires the reset token and new password
    - Validates the token and updates the password
    - Marks the token as used
    - Returns 200 OK on success
    - Raises 400 for invalid or expired tokens
    """
    # Find the token
    db_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == reset_data.token,
        PasswordResetToken.used == False,
        PasswordResetToken.expires_at > datetime.utcnow()
    ).first()
    
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    # Get the user
    user = db.query(DBUser).filter(DBUser.userID == db_token.user_id).first()
    if not user or user.deleted_bol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found or disabled"
        )
    
    # Update the password
    user.password_str = get_password_hash(reset_data.new_password)
    user.passChangeDate_dat = datetime.utcnow()
    
    # Mark token as used
    db_token.used = True
    db_token.used_at = datetime.utcnow()
    
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not reset password"
        )
    
    return {"message": "Password has been reset successfully"}

@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change the password for the authenticated user.
    
    - Requires current password and new password
    - Validates the current password
    - Updates the password
    - Returns 200 OK on success
    - Raises 400 for invalid current password
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update the password
    current_user.password_str = get_password_hash(password_data.new_password)
    current_user.passChangeDate_dat = datetime.utcnow()
    current_user.lastUpdateDate_dat = datetime.utcnow()
    
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not change password"
        )
    
    return {"message": "Password changed successfully"}

@router.get("/me", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: DBUser = Depends(get_current_user)
):
    """
    Get the profile of the authenticated user.
    
    - Returns user profile information
    - Requires valid authentication
    """
    return current_user

@router.post("/revoke-all-tokens", status_code=status.HTTP_200_OK)
async def revoke_all_tokens(
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Revoke all refresh tokens for the authenticated user.
    
    - Revokes all active refresh tokens for the user
    - Useful for security incidents or when changing sensitive information
    - Returns 200 OK on success
    """
    try:
        # Find all active tokens for the user
        active_tokens = db.query(RefreshToken).filter(
            RefreshToken.user_id == current_user.userID,
            RefreshToken.revoked == False
        ).all()
        
        # Revoke all tokens
        for token in active_tokens:
            token.revoked = True
            token.revoked_at = datetime.utcnow()
        
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not revoke tokens"
        )
    
    return {"message": f"Successfully revoked {len(active_tokens)} tokens"}
