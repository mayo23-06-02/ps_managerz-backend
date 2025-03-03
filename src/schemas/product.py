# src/schemas/product.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal

class ProductBase(BaseModel):
    productCode_str: str
    keyCode_int: int
    productCode_int: Optional[int] = None
    genericName_str: Optional[str] = None
    genericCode_str: Optional[str] = None
    strengthName_str: Optional[str] = None
    strengthCode_str: Optional[str] = None
    strengthValue_dbl: Optional[float] = None
    administration_str: Optional[str] = None
    packSizeUnit_str: Optional[str] = None
    packSizeValue_dbl: Optional[float] = None
    packSizeCode_str: Optional[str] = None
    packSizeDescription_str: Optional[str] = None
    description_str: Optional[str] = None
    descriptionShort_str: Optional[str] = None
    tradeName_str: Optional[str] = None
    form_str: Optional[str] = None
    formCode_str: Optional[str] = None
    route_str: Optional[str] = None
    department_str: str

class ProductCreate(ProductBase):
    isIncludeGenericInDescr_bol: Optional[bool] = False
    isIncludeTradeInDescr_bol: Optional[bool] = False
    swapGeneric4Trade_bol: Optional[bool] = False
    currentPackCost_mon: Optional[float] = None
    currencyCode_str: Optional[str] = None
    isReviewLevel_bol: Optional[bool] = False
    isPaediatric_bol: Optional[bool] = False
    isInjectible_bol: Optional[bool] = False
    isKeep_bol: Optional[bool] = False
    deleted_bol: Optional[bool] = False
    productID: Optional[UUID] = None

class ProductUpdate(BaseModel):
    genericName_str: Optional[str] = None
    genericCode_str: Optional[str] = None
    strengthName_str: Optional[str] = None
    strengthCode_str: Optional[str] = None
    strengthValue_dbl: Optional[float] = None
    administration_str: Optional[str] = None
    packSizeUnit_str: Optional[str] = None
    packSizeValue_dbl: Optional[float] = None
    packSizeCode_str: Optional[str] = None
    packSizeDescription_str: Optional[str] = None
    description_str: Optional[str] = None
    descriptionShort_str: Optional[str] = None
    isIncludeGenericInDescr_bol: Optional[bool] = None
    tradeName_str: Optional[str] = None
    isIncludeTradeInDescr_bol: Optional[bool] = None
    swapGeneric4Trade_bol: Optional[bool] = None
    form_str: Optional[str] = None
    formCode_str: Optional[str] = None
    route_str: Optional[str] = None
    packDescription_Str: Optional[str] = None
    extendedDescription_str: Optional[str] = None
    currentPackCost_mon: Optional[float] = None
    currencyCode_str: Optional[str] = None
    department_str: Optional[str] = None
    groupName_str: Optional[str] = None
    categoryGroup_str: Optional[str] = None
    isReviewLevel_bol: Optional[bool] = None
    ATC_str: Optional[str] = None
    ICD10Code_str: Optional[str] = None
    isPaediatric_bol: Optional[bool] = None
    isInjectible_bol: Optional[bool] = None
    isKeep_bol: Optional[bool] = None
    manufacturer_str: Optional[str] = None
    lastUpdateBy_str: Optional[str] = None

class ProductResponse(ProductBase):
    productID: Optional[UUID] = None
    isIncludeGenericInDescr_bol: Optional[bool] = None
    isIncludeTradeInDescr_bol: Optional[bool] = None
    swapGeneric4Trade_bol: Optional[bool] = None
    packDescription_Str: Optional[str] = None
    extendedDescription_str: Optional[str] = None
    currentPackCost_mon: Optional[float] = None
    currencyCode_str: Optional[str] = None
    groupName_str: Optional[str] = None
    categoryGroup_str: Optional[str] = None
    isReviewLevel_bol: Optional[bool] = None
    ATC_str: Optional[str] = None
    ICD10Code_str: Optional[str] = None
    isPaediatric_bol: Optional[bool] = None
    isInjectible_bol: Optional[bool] = None
    isKeep_bol: Optional[bool] = None
    lastQtyOnHand_int: Optional[int] = None
    manufacturer_str: Optional[str] = None
    lastUpdateDate_dat: Optional[datetime] = None
    lastUpdateBy_str: Optional[str] = None
    deleted_bol: Optional[bool] = None
    createdDate_dat: Optional[datetime] = None

    class Config:
        orm_mode = True

class ProductDelete(BaseModel):
    deletedDescr_str: Optional[str] = None
    lastUpdateBy_str: str

class ProductSearchParams(BaseModel):
    search: Optional[str] = None
    department: Optional[str] = None
    category: Optional[str] = None
    active_only: bool = True
    generic_name: Optional[str] = None
    trade_name: Optional[str] = None
    form: Optional[str] = None
    min_cost: Optional[float] = None
    max_cost: Optional[float] = None
    has_stock: Optional[bool] = None

class ProductResponseMessage(BaseModel):
    message: str
    product_code: str
