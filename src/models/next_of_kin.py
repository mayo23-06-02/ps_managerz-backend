# src/models/next_of_kin.py
from sqlalchemy import Column, String, Boolean, DateTime, LargeBinary, Text, ForeignKey
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER, NVARCHAR, IMAGE
from sqlalchemy.orm import relationship
from src.database.db import Base
from uuid import uuid4
from datetime import datetime

class ClientNextOfKin(Base):
    __tablename__ = 'tbClientNextOfKin'
    
    # Primary key
    OID = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid4)
    
    # Composite key fields
    firstName_str = Column(NVARCHAR(30), nullable=False)
    relationship_str = Column(NVARCHAR(70), nullable=False)
    clientOID = Column(UNIQUEIDENTIFIER, nullable=False)
    
    # Personal details
    lastName_str = Column(NVARCHAR(30), nullable=True)
    nationalIdNumber_str = Column(NVARCHAR(20), nullable=True)
    phoneNumber_str = Column(NVARCHAR(20), nullable=True)
    gender_str = Column(NVARCHAR(1), nullable=True)
    email_str = Column(NVARCHAR(70), nullable=True)
    
    # Address
    addressPhys01_str = Column(NVARCHAR(4000), nullable=True)
    addressPhys02_str = Column(NVARCHAR(4000), nullable=True)
    country_str = Column(NVARCHAR(30), nullable=True)
    
    # Metadata
    addedDate_dat = Column(DateTime, nullable=True, default=datetime.utcnow)
    addedUser_str = Column(NVARCHAR(150), nullable=True)
    lastUpdateDate_dat = Column(DateTime, nullable=True)
    lastUpdateBy_str = Column(NVARCHAR(150), nullable=True)
    
    # Soft delete fields
    deleted_bol = Column(Boolean, nullable=False, default=False)
    deletedBy_str = Column(NVARCHAR(150), nullable=True)
    deletetedReason_str = Column(NVARCHAR(250), nullable=True)
    
    # Additional fields
    photo_img = Column(IMAGE, nullable=True)
    notes_str = Column(Text, nullable=True)
    
    __table_args__ = (
        {'schema': 'dbo'}  # Assuming the schema is 'dbo'
    )
