from sqlalchemy import Column, String, DateTime, Float, Integer, Boolean
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.ext.declarative import declarative_base
from uuid import uuid4

Base = declarative_base()

class ClientAntropometric(Base):
    __tablename__ = "tbClientAntropometric"

    OID = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid4)
    createdBy_str = Column(String(150), nullable=True)
    systemDate_dat = Column(DateTime, nullable=False)
    clientOID = Column(UNIQUEIDENTIFIER, nullable=False)
    date_dat = Column(DateTime, nullable=False)
    weight_int = Column(Float, nullable=True)
    height_Int = Column(Float, nullable=True)
    idealWeight_int = Column(Integer, nullable=True)
    renalFunction_str = Column(String(30), nullable=True)
    crCC = Column(String(30), nullable=True)
    IBW_dbl = Column(Float, nullable=True)
    BMI_dbl = Column(Float, nullable=True)
    ABW_dbl = Column(Float, nullable=True)
    BSA_dbl = Column(Float, nullable=True)
    LBW_dbl = Column(Float, nullable=True)
    TBW_dbl = Column(Float, nullable=True)
    srCr_dbl = Column(Float, nullable=True)
    crCl_dbl = Column(Float, nullable=True)
    pulse_int = Column(Integer, nullable=True)
    temperature_dbl = Column(Float, nullable=True)
    BP_str = Column(String(7), nullable=True)
    MUAC_dbl = Column(Float, nullable=True)
    respiratoryRate_str = Column(String(30), nullable=True)
    WHOstage_str = Column(String(5), nullable=True)
    locked_bol = Column(Boolean, nullable=False)
    lockedBy_str = Column(String(150), nullable=True)
    lockedDate_dat = Column(DateTime, nullable=True)
    remarks_str = Column(String(200), nullable=True)
    posted_bol = Column(Boolean, nullable=True)
    postedDate_dat = Column(DateTime, nullable=True)
    postedBy_str = Column(String(150), nullable=True)
    postedBy_GUID = Column(UNIQUEIDENTIFIER, nullable=True)
    Rx_OID = Column(UNIQUEIDENTIFIER, nullable=True)
    machine_str = Column(String(100), nullable=True)
    machineID = Column(String(20), nullable=True)