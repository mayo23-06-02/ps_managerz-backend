# src/schemas/allergies.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from uuid import UUID
from datetime import datetime

class AllergyBase(BaseModel):
    allergyOID: UUID
    clientOID: UUID
    allergyName_str: Optional[str] = None
    allergySource_str: Optional[str] = None
    allergyDate_dat: Optional[datetime] = None
    allergyAuthicatedBy_Str: Optional[str] = None
    remarks_str: Optional[str] = None

class AllergyCreate(AllergyBase):
    OID: Optional[UUID] = None
    nonActive_bol: bool = False
    locked_bol: bool = False

class AllergyUpdate(BaseModel):
    allergyName_str: Optional[str] = None
    allergySource_str: Optional[str] = None
    allergyDate_dat: Optional[datetime] = None
    allergyAuthicatedBy_Str: Optional[str] = None
    remarks_str: Optional[str] = None
    nonActive_bol: Optional[bool] = None
    nonActiveDate_dat: Optional[datetime] = None
    locked_bol: Optional[bool] = None

class AllergyResponse(AllergyBase):
    OID: UUID
    nonActive_bol: bool
    nonActiveDate_dat: Optional[datetime] = None
    locked_bol: bool
    lockedBy_str: Optional[str] = None
    lockedDate_dat: Optional[datetime] = None
    posted_bol: Optional[bool] = None
    postedDate_dat: Optional[datetime] = None
    postedBy_str: Optional[str] = None
    postedBy_GUID: Optional[UUID] = None
    Rx_OID: Optional[UUID] = None
    machine_str: Optional[str] = None
    machineID: Optional[str] = None

    class Config:
        orm_mode = True

class AllergyLock(BaseModel):
    locked_bol: bool
    lockedBy_str: Optional[str] = None

class AllergyActivation(BaseModel):
    nonActive_bol: bool
    nonActiveDate_dat: Optional[datetime] = None

class AllergyPost(BaseModel):
    posted_bol: bool
    postedBy_str: Optional[str] = None
    postedBy_GUID: Optional[UUID] = None

class AllergyResponseMessage(BaseModel):
    message: str
    allergy_id: str
