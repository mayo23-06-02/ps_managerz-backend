# src/models/product.py
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, DECIMAL
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER, NVARCHAR, VARCHAR, MONEY, BIT
from sqlalchemy.orm import relationship
from src.database.db import Base
from uuid import uuid4
from datetime import datetime

class ProductMaster(Base):
    __tablename__ = 'tbProductMaster'
    
    # Primary key
    productCode_str = Column(NVARCHAR(25), primary_key=True)
    
    # Identifiers
    productID = Column(UNIQUEIDENTIFIER, default=uuid4, nullable=True)
    keyCode_int = Column(Integer, nullable=False)
    productCode_int = Column(Integer, nullable=True)
    
    # Product details
    genericName_str = Column(NVARCHAR(255), nullable=True)
    genericCode_str = Column(NVARCHAR(5), nullable=True)
    strengthName_str = Column(NVARCHAR(50), nullable=True)
    strengthCode_str = Column(NVARCHAR(4), nullable=True)
    strengthValue_dbl = Column(Float, nullable=True)
    administration_str = Column(NVARCHAR(50), nullable=True)
    
    # Pack details
    packSizeUnit_str = Column(NVARCHAR(50), nullable=True)
    packSizeValue_dbl = Column(Float, nullable=True)
    packSizeCode_str = Column(NVARCHAR(10), nullable=True)
    packSizeDescription_str = Column(NVARCHAR(30), nullable=True)
    packDescription_Str = Column(NVARCHAR(150), nullable=True)
    
    # Descriptions
    description_str = Column(VARCHAR(250), nullable=True)
    descriptionShort_str = Column(NVARCHAR(100), nullable=True)
    isIncludeGenericInDescr_bol = Column(BIT, nullable=True)
    tradeName_str = Column(NVARCHAR(80), nullable=True)
    isIncludeTradeInDescr_bol = Column(BIT, nullable=True)
    swapGeneric4Trade_bol = Column(BIT, nullable=True)
    extendedDescription_str = Column(NVARCHAR(250), nullable=True)
    descriptionLocal_str = Column(NVARCHAR(250), nullable=True)
    
    # Form and route
    form_str = Column(NVARCHAR(40), nullable=True)
    formCode_str = Column(NVARCHAR(4), nullable=True)
    route_str = Column(NVARCHAR(50), nullable=True)
    
    # Financial details
    currentPackCost_mon = Column(MONEY, nullable=True)
    currencyCode_str = Column(NVARCHAR(5), nullable=True)
    taxPerc_dbl = Column(Float, nullable=True)
    cacheOldPrice_dci = Column(DECIMAL(38, 2), nullable=True)
    
    # Codes and identifiers
    ICN_str = Column(NVARCHAR(25), nullable=True)
    ICN_count = Column(Integer, nullable=True)
    RCN_str = Column(NVARCHAR(14), nullable=True)
    FMSCode_str = Column(NVARCHAR(4), nullable=True)
    bin_str = Column(NVARCHAR(40), nullable=True)
    ATC_str = Column(NVARCHAR(7), nullable=True)
    ICD10Code_str = Column(NVARCHAR(15), nullable=True)
    wmisCode1_str = Column(NVARCHAR(20), nullable=True)
    wmisCode2_str = Column(NVARCHAR(20), nullable=True)
    
    # Classification
    levelOfUse_str = Column(NVARCHAR(3), nullable=True)
    instLevelOfUse_str = Column(NVARCHAR(3), nullable=True)
    orderType_str = Column(NVARCHAR(1), nullable=True)
    schedule_int = Column(Integer, nullable=True)
    department_str = Column(NVARCHAR(4), nullable=False)
    groupName_str = Column(NVARCHAR(50), nullable=True)
    categoryGroup_str = Column(NVARCHAR(50), nullable=True)
    line_str = Column(NVARCHAR(2), nullable=True)
    
    # Flags
    isReviewLevel_bol = Column(BIT, nullable=True)
    isPaediatric_bol = Column(BIT, nullable=True)
    isInjectible_bol = Column(BIT, nullable=True)
    isKeep_bol = Column(BIT, nullable=True)
    isLockedForIssuing_bol = Column(BIT, nullable=True)
    isCanBreak_bol = Column(BIT, nullable=True)
    flagClear_bol = Column(BIT, nullable=True)
    pushItem_bol = Column(BIT, nullable=True)
    showForm_bol = Column(BIT, nullable=True)
    tracer_bol = Column(BIT, nullable=True)
    lockedCycleCount_bol = Column(BIT, nullable=True)
    
    # Stock details
    lastStockCalcDate_dat = Column(DateTime, nullable=True)
    strengthRangePackCoefficient_dbl = Column(Float, nullable=True)
    maxStockAvailableInBudget_int = Column(Integer, nullable=True)
    stockAge_int = Column(Integer, nullable=True)
    lastQtyOnHand_int = Column(Integer, nullable=True)
    lastQtyOnRequest_int = Column(Integer, nullable=True)
    lastQtyOnHold_int = Column(Integer, nullable=True)
    lastQtyOnOrder_int = Column(Integer, nullable=True)
    lastQtyOnContract_int = Column(Integer, nullable=True)
    qtyOnHandSKU_dbl = Column(Float, nullable=True)
    
    # Transaction history
    lastOrderDate_dat = Column(DateTime, nullable=True)
    lastOrderRefNo_str = Column(NVARCHAR(40), nullable=True)
    lastReceiptDate_dat = Column(DateTime, nullable=True)
    lastReceiptRefNo_str = Column(NVARCHAR(40), nullable=True)
    lastIssueDate_dat = Column(DateTime, nullable=True)
    lastIssueRefNo_str = Column(NVARCHAR(40), nullable=True)
    lastStockTakeQty_int = Column(Integer, nullable=True)
    lastStockTakeDate_dat = Column(DateTime, nullable=True)
    lastStockTakeRefNo_str = Column(NVARCHAR(25), nullable=True)
    lastUnitsOnHand_dbl = Column(Float, nullable=True)
    lastDispensedValue_dbl = Column(Float, nullable=True)
    lastDispensedUnit_str = Column(NVARCHAR(50), nullable=True)
    lastBarCode_str = Column(NVARCHAR(30), nullable=True)
    lockedCycleCountRefNo_str = Column(NVARCHAR(25), nullable=True)
    
    # Physical attributes
    heightcm_dbl = Column(Float, nullable=True)
    lengthcm_dbl = Column(Float, nullable=True)
    widthcm_dbl = Column(Float, nullable=True)
    volumecm_dbl = Column(Float, nullable=True)
    
    # Additional info
    manufacturer_str = Column(NVARCHAR(70), nullable=True)
    flagClear_int = Column(Float, nullable=True)
    flagClear_str = Column(NVARCHAR(150), nullable=True)
    prodAbbreviation_str = Column(NVARCHAR(20), nullable=True)
    pushDescription_str = Column(NVARCHAR(250), nullable=True)
    supplement_str = Column(NVARCHAR(100), nullable=True)
    prodType_str = Column(NVARCHAR(1), nullable=True)
    barcodeScramble_txt = Column(NVARCHAR(4000), nullable=True)
    QRcode_str = Column(VARCHAR, nullable=True)
    
    # Audit fields
    lastUpdateDate_dat = Column(DateTime, nullable=True)
    lastUpdateBy_str = Column(NVARCHAR(150), nullable=True)
    deleted_bol = Column(BIT, nullable=True, default=False)
    deletedDescr_str = Column(NVARCHAR(200), nullable=True)
    deletedDate_dat = Column(DateTime, nullable=True)
    logReference_str = Column(NVARCHAR(50), nullable=True)
    createdDate_dat = Column(DateTime, nullable=True, default=datetime.utcnow)
    oldProductID = Column(UNIQUEIDENTIFIER, nullable=True)
    
    __table_args__ = (
        {'schema': 'dbo'}  # Assuming the schema is 'dbo'
    )
