from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import User as DBUser
from datetime import datetime
from uuid import UUID

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserCreate(BaseModel):
    systemKey_str: str
    password_str: str
    title_str: Optional[str] = None
    firstName_str: str
    lastName_str: str
    initials_str: Optional[str] = None
    position_str: Optional[str] = None
    facilitator_bol: Optional[bool] = None
    telephone_str: Optional[str] = None
    cellular_str: Optional[str] = None
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
    userName_str: Optional[str] = None
    universal_bol: Optional[bool] = None
    nationalIdNumber_str: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True

class UserGet(BaseModel):
    userID: UUID
    systemKey_str: str
    password_str: str
    title_str: Optional[str] = None
    firstName_str: str
    lastName_str: str
    initials_str: Optional[str] = None
    position_str: Optional[str] = None
    facilitator_bol: Optional[bool] = None
    telephone_str: Optional[str] = None
    cellular_str: Optional[str] = None
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
    userName_str: Optional[str] = None
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
            password_str=obj.password_str,
            title_str=obj.title_str,
            firstName_str=obj.firstName_str,
            lastName_str=obj.lastName_str,
            initials_str=obj.initials_str,
            position_str=obj.position_str,
            facilitator_bol=obj.facilitator_bol,
            telephone_str=obj.telephone_str,
            cellular_str=obj.cellular_str,
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
            userName_str=obj.userName_str,
            universal_bol=obj.universal_bol,
            nationalIdNumber_str=obj.nationalIdNumber_str
        )

class UserGetAll(BaseModel):
    userID: UUID
    systemKey_str: str
    password_str: str
    title_str: Optional[str] = None
    firstName_str: str
    lastName_str: str
    initials_str: Optional[str] = None
    position_str: Optional[str] = None
    facilitator_bol: Optional[bool] = None
    telephone_str: Optional[str] = None
    cellular_str: Optional[str] = None
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
    userName_str: Optional[str] = None
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
            password_str=obj.password_str,
            title_str=obj.title_str,
            firstName_str=obj.firstName_str,
            lastName_str=obj.lastName_str,
            initials_str=obj.initials_str,
            position_str=obj.position_str,
            facilitator_bol=obj.facilitator_bol,
            telephone_str=obj.telephone_str,
            cellular_str=obj.cellular_str,
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
            userName_str=obj.userName_str,
            universal_bol=obj.universal_bol,
            nationalIdNumber_str=obj.nationalIdNumber_str
        )

@app.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = DBUser(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "User created successfully", "user": str(db_user.userID)})

@app.get("/users/{user_id}", response_model=UserGet)
async def read_user(user_id: UUID, db: Session = Depends(get_db)):
    db_user = db.query(DBUser).filter(DBUser.userID == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserGet.from_orm(db_user)

@app.get("/users/", response_model=List[UserGetAll])
async def read_users(db: Session = Depends(get_db)):
    users = db.query(DBUser).all()
    return [UserGetAll.from_orm(user) for user in users]