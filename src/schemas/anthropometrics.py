# src/schemas/anthropometrics.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from uuid import UUID
from datetime import datetime

class AnthropometricsBase(BaseModel):
    clientOID: UUID
    date_dat: datetime
    weight_int: Optional[float] = None
    height_Int: Optional[float] = None
    idealWeight_int: Optional[int] = None
    renalFunction_str: Optional[str] = None
    crCC: Optional[str] = None
    IBW_dbl: Optional[float] = None
    BMI_dbl: Optional[float] = None
    ABW_dbl: Optional[float] = None
    BSA_dbl: Optional[float] = None
    LBW_dbl: Optional[float] = None
    TBW_dbl: Optional[float] = None
    srCr_dbl: Optional[float] = None
    crCl_dbl: Optional[float] = None
    pulse_int: Optional[int] = None
    temperature_dbl: Optional[float] = None
    BP_str: Optional[str] = None
    MUAC_dbl: Optional[float] = None
    respiratoryRate_str: Optional[str] = None
    WHOstage_str: Optional[str] = None
    remarks_str: Optional[str] = None
    Rx_OID: Optional[UUID] = None
    machine_str: Optional[str] = None
    machineID: Optional[str] = None

class AnthropometricsCreate(AnthropometricsBase):
    createdBy_str: Optional[str] = None
    locked_bol: bool = False

class AnthropometricsUpdate(BaseModel):
    date_dat: Optional[datetime] = None
    weight_int: Optional[float] = None
    height_Int: Optional[float] = None
    idealWeight_int: Optional[int] = None
    renalFunction_str: Optional[str] = None
    crCC: Optional[str] = None
    IBW_dbl: Optional[float] = None
    BMI_dbl: Optional[float] = None
    ABW_dbl: Optional[float] = None
    BSA_dbl: Optional[float] = None
    LBW_dbl: Optional[float] = None
    TBW_dbl: Optional[float] = None
    srCr_dbl: Optional[float] = None
    crCl_dbl: Optional[float] = None
    pulse_int: Optional[int] = None
    temperature_dbl: Optional[float] = None
    BP_str: Optional[str] = None
    MUAC_dbl: Optional[float] = None
    respiratoryRate_str: Optional[str] = None
    WHOstage_str: Optional[str] = None
    remarks_str: Optional[str] = None
    Rx_OID: Optional[UUID] = None
    machine_str: Optional[str] = None
    machineID: Optional[str] = None

class AnthropometricsResponse(AnthropometricsBase):
    OID: UUID
    createdBy_str: Optional[str] = None
    systemDate_dat: datetime
    locked_bol: bool
    lockedBy_str: Optional[str] = None
    lockedDate_dat: Optional[datetime] = None
    posted_bol: Optional[bool] = None
    postedDate_dat: Optional[datetime] = None
    postedBy_str: Optional[str] = None
    postedBy_GUID: Optional[UUID] = None

    class Config:
        orm_mode = True

class AnthropometricsLock(BaseModel):
    locked_bol: bool
    lockedBy_str: Optional[str] = None

class AnthropometricsPost(BaseModel):
    posted_bol: bool
    postedBy_str: Optional[str] = None
    postedBy_GUID: Optional[UUID] = None

class AnthropometricsResponseMessage(BaseModel):
    message: str
    anthropometrics_id: str
