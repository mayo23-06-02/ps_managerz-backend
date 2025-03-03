# src/api/v1/endpoints/products.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from uuid import UUID, uuid4
from typing import List, Optional
from datetime import datetime
from sqlalchemy import or_, and_, func

from src.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductDelete,
    ProductResponseMessage,
    ProductSearchParams
)
from src.database.session import get_db
from src.models.product import ProductMaster
from src.api.dependencies import get_current_user

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProductResponseMessage)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Create a new product in the product master.
    
    - Requires productCode_str, keyCode_int, and department_str
    - Automatically generates productID if not provided
    - Returns the created product code and a success message
    """
    # Check if product code already exists
    existing_product = db.query(ProductMaster).filter(ProductMaster.productCode_str == product.productCode_str).first()
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product with code {product.productCode_str} already exists"
        )
    
    # Create product instance
    db_product = ProductMaster(
        **product.dict(),
        productID=product.productID or uuid4(),
        createdDate_dat=datetime.utcnow(),
        lastUpdateDate_dat=datetime.utcnow(),
        lastUpdateBy_str=current_user.userName_str,
        deleted_bol=False
    )
    
    try:
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Database integrity error: {str(e)}"
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    
    return {
        "message": "Product created successfully",
        "product_code": db_product.productCode_str
    }

@router.get("/{product_code}", response_model=ProductResponse)
async def get_product(
    product_code: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve a product by its product code.
    
    - Returns the complete product information
    - Raises 404 if product not found
    """
    db_product = db.query(ProductMaster).filter(ProductMaster.productCode_str == product_code).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with code {product_code} not found"
        )
    
    return db_product

@router.get("/", response_model=List[ProductResponse])
async def get_products(
    skip: int = 0,
    limit: int = 100,
    department: Optional[str] = None,
    active_only: bool = True,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve products with optional filtering.
    
    - Supports pagination with skip/limit parameters
    - Can filter by department
    - Can filter active/deleted products
    - Can search by product code, description, or generic name
    - Returns an empty list if no products found
    """
    query = db.query(ProductMaster)
    
    # Apply filters
    if active_only:
        query = query.filter(or_(ProductMaster.deleted_bol.is_(None), ProductMaster.deleted_bol == False))
    
    if department:
        query = query.filter(ProductMaster.department_str == department)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                ProductMaster.productCode_str.ilike(search_term),
                ProductMaster.description_str.ilike(search_term),
                ProductMaster.genericName_str.ilike(search_term),
                ProductMaster.tradeName_str.ilike(search_term)
            )
        )
    
    # Apply pagination
    products = query.order_by(ProductMaster.productCode_str).offset(skip).limit(limit).all()
    
    return products

@router.put("/{product_code}", response_model=ProductResponseMessage)
async def update_product(
    product_code: str,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Update an existing product.
    
    - Requires product_code in the path
    - Updates only the fields provided in the request
    - Cannot update a deleted product
    - Returns the updated product code and a success message
    """
    db_product = db.query(ProductMaster).filter(ProductMaster.productCode_str == product_code).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with code {product_code} not found"
        )
    
    if db_product.deleted_bol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update a deleted product"
        )
    
    # Update product attributes
    update_data = product.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    # Update audit fields
    db_product.lastUpdateDate_dat = datetime.utcnow()
    db_product.lastUpdateBy_str = current_user.userName_str
    
    try:
        db.commit()
        db.refresh(db_product)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Database integrity error: {str(e)}"
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    
    return {
        "message": "Product updated successfully",
        "product_code": product_code
    }

@router.delete("/{product_code}", response_model=ProductResponseMessage)
async def delete_product(
    product_code: str,
    delete_data: ProductDelete,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Soft delete a product.
    
    - Requires product_code in the path
    - Sets deleted_bol to True
    - Records deletion description and who deleted it
    - Returns the deleted product code and a success message
    """
    db_product = db.query(ProductMaster).filter(ProductMaster.productCode_str == product_code).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with code {product_code} not found"
        )
    
    if db_product.deleted_bol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product is already deleted"
        )
    
    # Update delete fields
    db_product.deleted_bol = True
    db_product.deletedDescr_str = delete_data.deletedDescr_str
    db_product.deletedDate_dat = datetime.utcnow()
    db_product.lastUpdateDate_dat = datetime.utcnow()
    db_product.lastUpdateBy_str = delete_data.lastUpdateBy_str or current_user.userName_str
    
    try:
        db.commit()
        db.refresh(db_product)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    
    return {
        "message": "Product deleted successfully",
        "product_code": product_code
    }

@router.put("/restore/{product_code}", response_model=ProductResponseMessage)
async def restore_product(
    product_code: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Restore a soft-deleted product.
    
    - Requires product_code in the path
    - Sets deleted_bol back to False
    - Clears deletion fields
    - Returns the restored product code and a success message
    """
    db_product = db.query(ProductMaster).filter(ProductMaster.productCode_str == product_code).first()
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with code {product_code} not found"
        )
    
    if not db_product.deleted_bol:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product is not deleted"
        )
    
    # Restore product
    db_product.deleted_bol = False
    db_product.deletedDescr_str = None
    db_product.deletedDate_dat = None
    db_product.lastUpdateDate_dat = datetime.utcnow()
    db_product.lastUpdateBy_str = current_user.userName_str
    
    try:
        db.commit()
        db.refresh(db_product)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    
    return {
        "message": "Product restored successfully",
        "product_code": product_code
    }

@router.post("/search", response_model=List[ProductResponse])
async def search_products(
    search_params: ProductSearchParams,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Advanced search for products.
    
    - Supports multiple search criteria
    - Supports pagination with skip/limit parameters
    - Returns an empty list if no products found
    """
    query = db.query(ProductMaster)
    
    # Apply filters based on search parameters
    if search_params.active_only:
        query = query.filter(or_(ProductMaster.deleted_bol.is_(None), ProductMaster.deleted_bol == False))
    
    if search_params.department:
        query = query.filter(ProductMaster.department_str == search_params.department)
    
    if search_params.category:
        query = query.filter(ProductMaster.categoryGroup_str == search_params.category)
    
    if search_params.generic_name:
        query = query.filter(ProductMaster.genericName_str.ilike(f"%{search_params.generic_name}%"))
    
    if search_params.trade_name:
        query = query.filter(ProductMaster.tradeName_str.ilike(f"%{search_params.trade_name}%"))
    
    if search_params.form:
        query = query.filter(ProductMaster.form_str.ilike(f"%{search_params.form}%"))
    
    if search_params.min_cost is not None:
        query = query.filter(ProductMaster.currentPackCost_mon >= search_params.min_cost)
    
    if search_params.max_cost is not None:
        query = query.filter(ProductMaster.currentPackCost_mon <= search_params.max_cost)
    
    if search_params.has_stock is not None:
        if search_params.has_stock:
            query = query.filter(ProductMaster.lastQtyOnHand_int > 0)
        else:
            query = query.filter(or_(
                ProductMaster.lastQtyOnHand_int.is_(None),
                ProductMaster.lastQtyOnHand_int == 0
            ))
    
    if search_params.search:
        search_term = f"%{search_params.search}%"
        query = query.filter(
            or_(
                ProductMaster.productCode_str.ilike(search_term),
                ProductMaster.description_str.ilike(search_term),
                ProductMaster.genericName_str.ilike(search_term),
                ProductMaster.tradeName_str.ilike(search_term),
                ProductMaster.ATC_str.ilike(search_term)
            )
        )
    
    # Apply pagination
    products = query.order_by(ProductMaster.productCode_str).offset(skip).limit(limit).all()
    
    return products

@router.get("/department/{department_code}", response_model=List[ProductResponse])
async def get_products_by_department(
    department_code: str,
    active_only: bool = True,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve products for a specific department.
    
    - Filters by department code
    - Can filter active/deleted products
    - Supports pagination with skip/limit parameters
    - Returns an empty list if no products found
    """
    query = db.query(ProductMaster).filter(ProductMaster.department_str == department_code)
    
    if active_only:
        query = query.filter(or_(ProductMaster.deleted_bol.is_(None), ProductMaster.deleted_bol == False))
    
    products = query.order_by(ProductMaster.productCode_str).offset(skip).limit(limit).all()
    
    return products

@router.get("/category/{category}", response_model=List[ProductResponse])
async def get_products_by_category(
    category: str,
    active_only: bool = True,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve products for a specific category.
    
    - Filters by category group
    - Can filter active/deleted products
    - Supports pagination with skip/limit parameters
    - Returns an empty list if no products found
    """
    query = db.query(ProductMaster).filter(ProductMaster.categoryGroup_str == category)
    
    if active_only:
        query = query.filter(or_(ProductMaster.deleted_bol.is_(None), ProductMaster.deleted_bol == False))
    
    products = query.order_by(ProductMaster.productCode_str).offset(skip).limit(limit).all()
    
    return products
