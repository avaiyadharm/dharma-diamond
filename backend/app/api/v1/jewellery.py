from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.core.permissions import UserRole
from app.schemas.jewellery import (
    JewelleryProductCreate, JewelleryProductUpdate, JewelleryProductOut,
    JewelleryItemCreate, JewelleryItemUpdate, JewelleryItemOut
)
from app.api.deps import get_current_user, require_roles
from app.services import jewellery_service

router = APIRouter(prefix="/jewellery", tags=["Jewellery"])

# --- Catalog / Designs ---
@router.get("/products", response_model=Dict[str, Any])
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    category: Optional[str] = None,
    metal_type: Optional[str] = None,
    purity: Optional[str] = None,
    query: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return jewellery_service.get_jewellery_products(
        db=db,
        skip=skip,
        limit=limit,
        category=category,
        metal_type=metal_type,
        purity=purity,
        query=query
    )

@router.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(
    product_in: JewelleryProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    return jewellery_service.create_jewellery_product(db, product_in, current_user.id)

# --- Serialized Physical Items ---
@router.get("/items", response_model=Dict[str, Any])
def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    category: Optional[str] = None,
    metal_type: Optional[str] = None,
    status: Optional[str] = None,
    location_id: Optional[str] = None,
    product_id: Optional[str] = None,
    query: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return jewellery_service.get_jewellery_items(
        db=db,
        skip=skip,
        limit=limit,
        category=category,
        metal_type=metal_type,
        status=status,
        location_id=location_id,
        product_id=product_id,
        query=query
    )

@router.post("/items", status_code=status.HTTP_201_CREATED)
def add_item(
    item_in: JewelleryItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    return jewellery_service.create_jewellery_item(db, item_in, current_user.id)

@router.get("/items/{item_id}")
def get_item(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = jewellery_service.get_jewellery_item_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jewellery item not found")
    
    return {
        "id": item.id,
        "sku": item.sku,
        "product_id": item.product_id,
        "gross_weight_grams": item.gross_weight_grams,
        "net_metal_weight_grams": item.net_metal_weight_grams,
        "total_stone_carats": item.total_stone_carats,
        "hallmark_details": item.hallmark_details,
        "metal_cost": item.metal_cost,
        "stone_cost": item.stone_cost,
        "making_charge": item.making_charge,
        "other_costs": item.other_costs,
        "total_cost": item.total_cost,
        "selling_price": item.selling_price,
        "status": item.status,
        "location_id": item.location_id,
        "supplier_id": item.supplier_id,
        "image_url": item.image_url or item.product.image_url,
        "notes": item.notes,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
        "product_name": item.product.name,
        "product_category": item.product.category,
        "design_code": item.product.design_code,
        "metal_type": item.product.metal_type,
        "purity": item.product.purity,
        "location_name": item.location.name if item.location else None,
        "supplier_name": item.supplier.business_name if item.supplier else None,
        "stones": [
            {
                "id": st.id,
                "stone_type": st.stone_type,
                "diamond_id": st.diamond_id,
                "stone_count": st.stone_count,
                "carat_weight": st.carat_weight,
                "shape": st.shape,
                "color": st.color,
                "clarity": st.clarity,
                "setting_type": st.setting_type
            } for st in item.stones
        ]
    }

@router.put("/items/{item_id}")
def edit_item(
    item_id: str,
    item_in: JewelleryItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    return jewellery_service.update_jewellery_item(db, item_id, item_in, current_user.id)
