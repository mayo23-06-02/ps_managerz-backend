from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional

class ClientAntropometricCreate(BaseModel):
    createdBy_str: Optional[str]
    systemDate_dat: datetime
    clientOID: UUID
    date_dat: datetime
    weight_int: Optional[float]
    height_Int: Optional[float]
    idealWeight_int: Optional[int]
    renalFunction_str: Optional[str]
    crCC: Optional[str]
    IBW_dbl: Optional[float]
    BMI_dbl: Optional[float]
    ABW_dbl: Optional[float]
    BSA_dbl: Optional[float]
    LBW_dbl: Optional[float]
    TBW_dbl: Optional[float]
    srCr_dbl: Optional[float]
    crCl_dbl: Optional[float]
    pulse_int: Optional[int]
    temperature_dbl: Optional[float]
    BP_str: Optional[str]
    MUAC_dbl: Optional[float]
    respiratoryRate_str: Optional[str]
    WHOstage_str: Optional[str]
    locked_bol: bool
    lockedBy_str: Optional[str]
    lockedDate_dat: Optional[datetime]
    remarks_str: Optional[str]
    posted_bol: Optional[bool]
    postedDate_dat: Optional[datetime]
    postedBy_str: Optional[str]
    postedBy_GUID: Optional[UUID]
    Rx_OID: Optional[UUID]
    machine_str: Optional[str]
    machineID: Optional[str]

class ClientAntropometricGetAll(ClientAntropometricCreate):
    OID: UUID

    class Config:
        orm_mode = True