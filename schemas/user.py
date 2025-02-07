from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime

class UserCreate(BaseModel):
    systemKey_str: str = Field(..., max_length=20)
    userName_str: str = Field(..., max_length=15)
    password_str: str = Field(..., max_length=250)
    title_str: Optional[str] = Field(None, max_length=15)
    firstName_str: Optional[str] = Field(None, max_length=50)
    lastName_str: str = Field(..., max_length=50)
    initials_str: Optional[str] = Field(None, max_length=20)
    position_str: Optional[str] = Field(None, max_length=50)
    facilitator_bol: Optional[bool] = None
    telephone_str: Optional[str] = Field(None, max_length=30)
    cellular_str: Optional[str] = Field(None, max_length=30)
    email_str: Optional[EmailStr] = None
    userNo_int: int
    deleted_bol: Optional[bool] = None
    deletedDate_dat: Optional[datetime] = None
    deletedBy_str: Optional[str] = Field(None, max_length=100)
    lastUpdateDate_dat: datetime
    lastUpdateBy_str: str = Field(..., max_length=100)
    passChangeDate_dat: Optional[datetime] = None
    exchangeAddress_str: Optional[str] = Field(None, max_length=150)
    colorDef_str: Optional[str] = Field(None, max_length=25)
    defPrescriber: Optional[UUID] = None
    defCustomerOID: Optional[UUID] = None
    employeeID: Optional[UUID] = None
    QRcode_str: Optional[str] = None
    universal_bol: Optional[bool] = None
    nationalIdNumber_str: Optional[str] = Field(None, max_length=20)

    class Config:
        orm_mode = True

class UserGetAll(BaseModel):
    userID: UUID
    systemKey_str: str
    userName_str: str
    password_str: str
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
    deletedDate_dat: Optional[str] = None
    deletedBy_str: Optional[str] = None
    lastUpdateDate_dat: str
    lastUpdateBy_str: str
    passChangeDate_dat: Optional[str] = None
    exchangeAddress_str: Optional[str] = None
    colorDef_str: Optional[str] = None
    defPrescriber: Optional[UUID] = None
    defCustomerOID: Optional[UUID] = None
    employeeID: Optional[UUID] = None
    QRcode_str: Optional[str] = None
    universal_bol: Optional[bool] = None
    nationalIdNumber_str: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        return cls(
            userID=obj.userID,
            systemKey_str=obj.systemKey_str,
            userName_str=obj.userName_str,
            password_str=obj.password_str,
            title_str=obj.title_str,
            firstName_str=obj.firstName_str,
            lastName_str=obj.lastName_str,
            initials_str=obj.initials_str,
            position_str=obj.position_str,
            facilitator_bol=obj.facilitator_bol,
            telephone_str=obj.telephone_str,
            cellular_str=obj.cellular_str,
            email_str=obj.email_str,
            userNo_int=obj.userNo_int,
            deleted_bol=obj.deleted_bol,
            deletedDate_dat=obj.deletedDate_dat.isoformat() if obj.deletedDate_dat else None,
            deletedBy_str=obj.deletedBy_str,
            lastUpdateDate_dat=obj.lastUpdateDate_dat.isoformat(),
            lastUpdateBy_str=obj.lastUpdateBy_str,
            passChangeDate_dat=obj.passChangeDate_dat.isoformat() if obj.passChangeDate_dat else None,
            exchangeAddress_str=obj.exchangeAddress_str,
            colorDef_str=obj.colorDef_str,
            defPrescriber=obj.defPrescriber,
            defCustomerOID=obj.defCustomerOID,
            employeeID=obj.employeeID,
            QRcode_str=obj.QRcode_str,
            universal_bol=obj.universal_bol,
            nationalIdNumber_str=obj.nationalIdNumber_str
        )