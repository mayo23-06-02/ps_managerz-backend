# src/models/anthropometrics.py
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER, BIT
from sqlalchemy.orm import relationship
from src.database.db import Base
from uuid import uuid4
from datetime import datetime

class ClientAnthropometrics(Base):
    __tablename__ = 'tbClientAntropometrics'
    
    # Primary key columns
    OID = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid4)
    clientOID = Column(UNIQUEIDENTIFIER, nullable=False, index=True)
    date_dat = Column(DateTime, nullable=False, index=True)
    
    # Metadata columns
    createdBy_str = Column(String(150), nullable=True)
    systemDate_dat = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Anthropometric measurements
    weight_int = Column(Float, nullable=True)
    height_Int = Column(Float, nullable=True)
    idealWeight_int = Column(Integer, nullable=True)
    renalFunction_str = Column(String(30), nullable=True)
    crCC = Column(String(30), nullable=True)
    IBW_dbl = Column(Float, nullable=True)
    BMI_dbl = Column(Float, nullable=True)
    ABW_dbl = Column(Float, nullable=True)
    BSA_dbl = Column(Float, nullable=True)
    LBW_dbl = Column(Float, nullable=True)
    TBW_dbl = Column(Float, nullable=True)
    srCr_dbl = Column(Float, nullable=True)
    crCl_dbl = Column(Float, nullable=True)
    
    # Vital signs
    pulse_int = Column(Integer, nullable=True)
    temperature_dbl = Column(Float, nullable=True)
    BP_str = Column(String(7), nullable=True)
    MUAC_dbl = Column(Float, nullable=True)
    respiratoryRate_str = Column(String(30), nullable=True)
    WHOstage_str = Column(String(5), nullable=True)
    
    # Record status
    locked_bol = Column(BIT, nullable=False, default=False)
    lockedBy_str = Column(String(150), nullable=True)
    lockedDate_dat = Column(DateTime, nullable=True)
    remarks_str = Column(String(200), nullable=True)
    posted_bol = Column(BIT, nullable=True)
    postedDate_dat = Column(DateTime, nullable=True)
    postedBy_str = Column(String(150), nullable=True)
    postedBy_GUID = Column(UNIQUEIDENTIFIER, nullable=True)
    
    # Additional references
    Rx_OID = Column(UNIQUEIDENTIFIER, nullable=True)
    machine_str = Column(String(100), nullable=True)
    machineID = Column(String(20), nullable=True)
