# src/models/auth.py
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship
from src.database.db import Base
from uuid import uuid4
from datetime import datetime, timedelta

class RefreshToken(Base):
    __tablename__ = 'tbRefreshTokens'
    
    id = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid4)
    user_id = Column(UNIQUEIDENTIFIER, nullable=False)
    token = Column(String(255), nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    revoked = Column(Boolean, nullable=False, default=False)
    revoked_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        {'schema': 'dbo'}
    )

class PasswordResetToken(Base):
    __tablename__ = 'tbPasswordResetTokens'
    
    id = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid4)
    user_id = Column(UNIQUEIDENTIFIER, nullable=False)
    token = Column(String(255), nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    used = Column(Boolean, nullable=False, default=False)
    used_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        {'schema': 'dbo'}
    )
