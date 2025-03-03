# src/schemas/client.py
from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime

class ClientBase(BaseModel):
    systemKey_str: str
    customerCode_str: Optional[str] = None
    customerID: int
    customerOID: Optional[UUID] = None
    lastName_str: Optional[str] = None
    firstName_str: Optional[str] = None
    nationalIdNumber_str: Optional[str] = None
    registrationDate_dat: Optional[datetime] = None
    customerInternalNo_CIN: Optional[str] = None
    registrationNo_str: str
    birthDate_dat: Optional[datetime] = None
    entryServicePoint: Optional[str] = None
    otherName_str: Optional[str] = None
    initials_str: Optional[str] = None
    gender_str: Optional[str] = None
    clientDescription_str: Optional[str] = None
    maritalStatus_str: Optional[str] = None
    classification_str: Optional[str] = None
    phoneNumber_str: Optional[str] = None
    email_str: Optional[str] = None
    addressPostal_str: Optional[str] = None
    addressPostalCity_str: Optional[str] = None
    addressResidential_str: Optional[str] = None
    active_bol: bool
    inActiveReason_str: Optional[str] = None
    addedDate_dat: Optional[datetime] = None
    addedUser_str: Optional[str] = None
    lastUpdateDate_dat: Optional[datetime] = None
    lastUpdateBy_str: Optional[str] = None
    cacheVisitDate_dat: Optional[datetime] = None
    deleted_bol: Optional[bool] = None
    deletedBy_str: Optional[str] = None
    deletetedReason_str: Optional[str] = None
    clientPhoto_img: Optional[str] = None
    flagPrintCol_bol: Optional[bool] = None
    deletedDate_dat: Optional[datetime] = None
    cacheCustName_str: Optional[str] = None
    seqINT: int
    entryServicePointOID: Optional[UUID] = None
    QRcode_str: Optional[str] = None
    passportTravelNo_str: Optional[str] = None
    locked_bol: Optional[bool] = None
    lockedBy_str: Optional[str] = None
    lockedDate_dat: Optional[datetime] = None
    lockedMachine_str: Optional[str] = None
    nationality_str: Optional[str] = None
    cacheVaccine_str: Optional[str] = None
    cacheVacCard_bol: Optional[bool] = None
    machine_str: Optional[str] = None
    machineID: Optional[str] = None
    notes_str: Optional[str] = None
    extSysOID_ART: Optional[UUID] = None
    regionLocale_str: Optional[str] = None
    religion_str: Optional[str] = None
    ethnicity_str: Optional[str] = None
    birthDate_calcYN: Optional[bool] = None
    cache_ageBandStr: Optional[str] = None

class ClientCreate(ClientBase):
    OID: Optional[UUID] = None  # Optional for IDENTITY_INSERT

class ClientUpdate(ClientBase):
    # All fields optional for partial updates
    systemKey_str: Optional[str] = None
    customerCode_str: Optional[str] = None
    customerID: Optional[int] = None
    registrationNo_str: Optional[str] = None
    active_bol: Optional[bool] = None
    seqINT: Optional[int] = None

class ClientGetAll(ClientBase):
    OID: UUID

    class Config:
        from_attributes = True  # For Pydantic v2 ORM mapping