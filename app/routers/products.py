from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert , select
from typing import List
from app.db.database import get_db
from app.db.models import Product
from app.schemas.product import ProductCreate, ProductResponse
from app.core.auth import get_current_user
from app.db.models import User


router = APIRouter( prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse)
async def create_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):

    new_product = Product(
        name=product.name,
        price=product.price,
        user_id = current_user.id
    )

    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product



@router.get("/", response_model=List[ProductResponse])
async def get_products(
    skip: int = 0,
    limit: int = 10,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    stmt = select(Product).where(Product.user_id == current_user.id)
    
    if search:
        stmt = stmt.where(Product.name.ilike(f"%{search}%"))

    stmt = stmt.offset(skip).limit(limit)

    result = await db.execute(stmt)
    products = result.scalars().all()

    if products is None:
        raise HTTPException(status_code=404, detail="Products not found")

    return products


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    stmt = select(Product).where(Product.id == product_id)
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not allowed to view this product")

    return product



@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):

    # 1️⃣ Find product
    stmt = select(Product).where(Product.id == product_id)
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to modify this product")


    # 2️⃣ Update product fields
    product.name = data.name
    product.price = data.price

    # 3️⃣ Save changes
    await db.commit()
    await db.refresh(product)

    return product



@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # 1️⃣ Find product first
    stmt = select(Product).where(Product.id == product_id)
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to modify this product")

    # 2️⃣ Delete it
    await db.delete(product)
    await db.commit()

    return {"message": "Product deleted successfully"}
