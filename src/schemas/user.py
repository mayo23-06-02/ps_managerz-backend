# src/schemas/user.py
from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    systemKey_str: str
    userName_str: str
    title_str: Optional[str] = None
    firstName_str: Optional[str] = None
    lastName_str: str
    initials_str: Optional[str] = None
    position_str: Optional[str] = None
    facilitator_bol: Optional[bool] = None
    telephone_str: Optional[str] = None
    cellular_str: Optional[str] = None
    email_str: Optional[str] = None
    userNo_int: int
    deleted_bol: Optional[bool] = None
    deletedDate_dat: Optional[datetime] = None
    deletedBy_str: Optional[str] = None
    lastUpdateDate_dat: datetime
    lastUpdateBy_str: str
    passChangeDate_dat: Optional[datetime] = None
    exchangeAddress_str: Optional[str] = None
    colorDef_str: Optional[str] = None
    defPrescriber: Optional[UUID] = None
    defCustomerOID: Optional[UUID] = None
    employeeID: Optional[UUID] = None
    QRcode_str: Optional[str] = None
    universal_bol: Optional[bool] = None
    nationalIdNumber_str: Optional[str] = None

class UserCreate(UserBase):
    password_str: str  # Plaintext password to be hashed
    userID: Optional[UUID] = None  # Optional for IDENTITY_INSERT

class UserGetAll(UserBase):
    userID: UUID

    class Config:
        from_attributes = True  # Updated for Pydantic v2 to map ORM objects