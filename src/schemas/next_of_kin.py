# src/schemas/next_of_kin.py
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from uuid import UUID
from datetime import datetime

class NextOfKinBase(BaseModel):
    firstName_str: str
    lastName_str: Optional[str] = None
    relationship_str: str
    clientOID: UUID
    nationalIdNumber_str: Optional[str] = None
    phoneNumber_str: Optional[str] = None
    gender_str: Optional[str] = None
    email_str: Optional[str] = None
    addressPhys01_str: Optional[str] = None
    addressPhys02_str: Optional[str] = None
    country_str: Optional[str] = None
    notes_str: Optional[str] = None

    @validator('gender_str')
    def validate_gender(cls, v):
        if v and v not in ['M', 'F', 'O']:
            raise ValueError('Gender must be M, F, or O')
        return v

class NextOfKinCreate(NextOfKinBase):
    addedUser_str: Optional[str] = None

class NextOfKinUpdate(BaseModel):
    firstName_str: Optional[str] = None
    lastName_str: Optional[str] = None
    relationship_str: Optional[str] = None
    nationalIdNumber_str: Optional[str] = None
    phoneNumber_str: Optional[str] = None
    gender_str: Optional[str] = None
    email_str: Optional[str] = None
    addressPhys01_str: Optional[str] = None
    addressPhys02_str: Optional[str] = None
    country_str: Optional[str] = None
    notes_str: Optional[str] = None
    lastUpdateBy_str: Optional[str] = None

    @validator('gender_str')
    def validate_gender(cls, v):
        if v and v not in ['M', 'F', 'O']:
            raise ValueError('Gender must be M, F, or O')
        return v

class NextOfKinDelete(BaseModel):
    deletedBy_str: str
    deletetedReason_str: Optional[str] = None

class NextOfKinResponse(NextOfKinBase):
    OID: UUID
    addedDate_dat: Optional[datetime] = None
    addedUser_str: Optional[str] = None
    lastUpdateDate_dat: Optional[datetime] = None
    lastUpdateBy_str: Optional[str] = None
    deleted_bol: bool
    deletedBy_str: Optional[str] = None
    deletetedReason_str: Optional[str] = None
    # photo_img is excluded as it's binary data

    class Config:
        orm_mode = True

class NextOfKinResponseMessage(BaseModel):
    message: str
    next_of_kin_id: str
