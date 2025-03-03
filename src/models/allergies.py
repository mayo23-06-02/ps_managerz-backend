# src/models/allergies.py
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER, BIT
from sqlalchemy.orm import relationship
from src.database.db import Base
from uuid import uuid4
from datetime import datetime

class ClientAllergy(Base):
    __tablename__ = 'tbClientAllergies'
    
    # Primary key columns
    OID = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid4)
    allergyOID = Column(UNIQUEIDENTIFIER, nullable=False)
    clientOID = Column(UNIQUEIDENTIFIER, nullable=False)
    
    # Allergy details
    allergyAuthicatedBy_Str = Column(String(250), nullable=True)
    allergyName_str = Column(String(100), nullable=True)
    allergySource_str = Column(String(150), nullable=True)
    allergyDate_dat = Column(DateTime, nullable=True)
    
    # Status columns
    nonActive_bol = Column(Boolean, nullable=False, default=False)
    nonActiveDate_dat = Column(DateTime, nullable=True)
    locked_bol = Column(Boolean, nullable=False, default=False)
    lockedBy_str = Column(String(150), nullable=True)
    lockedDate_dat = Column(DateTime, nullable=True)
    remarks_str = Column(String(200), nullable=True)
    posted_bol = Column(Boolean, nullable=True)
    postedDate_dat = Column(DateTime, nullable=True)
    postedBy_str = Column(String(150), nullable=True)
    postedBy_GUID = Column(UNIQUEIDENTIFIER, nullable=True)
    Rx_OID = Column(UNIQUEIDENTIFIER, nullable=True)
    machine_str = Column(String(100), nullable=True)
    machineID = Column(String(20), nullable=True)
    
    # Define composite unique constraint for allergyOID and clientOID
    __table_args__ = (
        {'schema': 'dbo'}  # Assuming the schema is 'dbo'
    )
