# src/models/allergies_history.py
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER, NVARCHAR
from sqlalchemy.orm import relationship
from src.database.db import Base
from uuid import uuid4
from datetime import datetime

class ClientAllergyEditHistory(Base):
    __tablename__ = 'tbClientAllergiesItemsEditHistory'
    
    # Primary key column
    OID = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid4)
    
    # Edit details
    editDescription1_str = Column(NVARCHAR(4000), nullable=True)
    editDescription2_str = Column(NVARCHAR(4000), nullable=True)
    productCode_int = Column(Integer, nullable=True)
    username_str = Column(NVARCHAR(100), nullable=True)
    userID = Column(UNIQUEIDENTIFIER, nullable=True)
    lastUpdateDate_dat = Column(DateTime, nullable=True, default=datetime.utcnow)
    
    # Reference columns
    itemsOID = Column(UNIQUEIDENTIFIER, nullable=True)  # Reference to the allergy record
    transactOID = Column(UNIQUEIDENTIFIER, nullable=True)
    
    # Machine info
    machine_str = Column(NVARCHAR(100), nullable=True)
    machineID = Column(NVARCHAR(20), nullable=True)
    
    __table_args__ = (
        {'schema': 'dbo'}  # Assuming the schema is 'dbo'
    )
