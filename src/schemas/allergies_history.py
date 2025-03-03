# src/schemas/allergies_history.py
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class AllergyHistoryBase(BaseModel):
    editDescription1_str: Optional[str] = None
    editDescription2_str: Optional[str] = None
    productCode_int: Optional[int] = None
    username_str: Optional[str] = None
    userID: Optional[UUID] = None
    itemsOID: Optional[UUID] = None
    transactOID: Optional[UUID] = None
    machine_str: Optional[str] = None
    machineID: Optional[str] = None

class AllergyHistoryCreate(AllergyHistoryBase):
    pass

class AllergyHistoryResponse(AllergyHistoryBase):
    OID: UUID
    lastUpdateDate_dat: Optional[datetime] = None

    class Config:
        orm_mode = True
