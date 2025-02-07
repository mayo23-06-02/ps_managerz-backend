from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship
from database import Base
from uuid import uuid4

class User(Base):
    __tablename__ = 'tbSystem_Users'

    userID = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid4)
    systemKey_str = Column(String(20), nullable=False)
    userName_str = Column(String(15), nullable=False, unique=True)
    password_str = Column(String(250), nullable=False)
    title_str = Column(String(15), nullable=True)
    firstName_str = Column(String(50), nullable=True)
    lastName_str = Column(String(50), nullable=False)
    initials_str = Column(String(20), nullable=True)
    position_str = Column(String(50), nullable=True)
    facilitator_bol = Column(Boolean, nullable=True)
    telephone_str = Column(String(30), nullable=True)
    cellular_str = Column(String(30), nullable=True)
    email_str = Column(String(100), nullable=True)
    userNo_int = Column(Integer, nullable=False)
    deleted_bol = Column(Boolean, nullable=True)
    deletedDate_dat = Column(DateTime, nullable=True)
    deletedBy_str = Column(String(100), nullable=True)
    lastUpdateDate_dat = Column(DateTime, nullable=False)
    lastUpdateBy_str = Column(String(100), nullable=False)
    passChangeDate_dat = Column(DateTime, nullable=True)
    exchangeAddress_str = Column(String(150), nullable=True)
    colorDef_str = Column(String(25), nullable=True)
    defPrescriber = Column(UNIQUEIDENTIFIER, nullable=True)
    defCustomerOID = Column(UNIQUEIDENTIFIER, nullable=True)
    employeeID = Column(UNIQUEIDENTIFIER, nullable=True)
    QRcode_str = Column(String(100), nullable=True)
    universal_bol = Column(Boolean, nullable=True)
    nationalIdNumber_str = Column(String(20), nullable=True)