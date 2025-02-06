from sqlalchemy import Column, String, Integer, Boolean, DateTime, UniqueConstraint, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER

Base = declarative_base()

class User(Base):
    __tablename__ = "tbSystem_Users"
    
    userID = Column(UNIQUEIDENTIFIER, primary_key=True, nullable=False)  # Primary key
    systemKey_str = Column(String(20), nullable=False)  # systemKey_str
    userName_str = Column(String(15), nullable=False)  # username
    password_str = Column(String(250), nullable=False)  # password_str
    title_str = Column(String(15))  # title_str
    firstName_str = Column(String(50))  # firstName_str
    lastName_str = Column(String(50), nullable=False)  # lastName_str
    initials_str = Column(String(20))  # initials_str
    position_str = Column(String(50))  # position_str
    facilitator_bol = Column(Boolean)  # facilitator_bol
    telephone_str = Column(String(30))  # telephone_str
    cellular_str = Column(String(30))  # cellular_str
    email_str = Column(String(50))  # email
    userNo_int = Column(Integer, nullable=False)  # userNo_int
    deleted_bol = Column(Boolean)  # deleted_bol
    deletedDate_dat = Column(DateTime)  # deletedDate_dat
    deletedBy_str = Column(String(100))  # deletedBy_str
    lastUpdateDate_dat = Column(DateTime, nullable=False)  # lastUpdateDate_dat
    lastUpdateBy_str = Column(String(100))  # lastUpdateBy_str
    passChangeDate_dat = Column(DateTime)  # passChangeDate_dat
    exchangeAddress_str = Column(String(150))  # exchangeAddress_str
    colorDef_str = Column(String(25))  # colorDef_str
    defPrescriber = Column(UNIQUEIDENTIFIER, nullable=True, unique=True)  # defPrescriber
    defCustomerOID = Column(UNIQUEIDENTIFIER, nullable=True, unique=True)  # defCustomerOID
    employeeID = Column(UNIQUEIDENTIFIER, nullable=True, unique=True)  # employeeID
    QRcode_str = Column(String, nullable=True)  # QRcode_str
    universal_bol = Column(Boolean)  # universal_bol
    nationalIdNumber_str = Column(String(20), nullable=False)  # nationalIdNumber_str

    __table_args__ = (UniqueConstraint('userName_str', 'email_str'),)  # Example constraint