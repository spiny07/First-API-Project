from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import User, Product
from app.core.auth import require_admin


router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/dashboard")
async def admin_dashboard(
        db: AsyncSession = Depends(get_db),
        admin = Depends(require_admin)
):
    
    user_count = await db.scalar(select(func.count(User.id)))

    product_count = await db.scalar(select(func.count(Product.id)))

    result = await db.execute(
        select(User.email, func.count(Product.id))
        .join(Product, Product.user_id == User.id, isouter=True)
        .group_by(User.email)
    )

    product_per_user = [
        {"email": email, "products": count}
        for email, count in result.all()
    ]

    return{
        "total_user": user_count,
        "total_product": product_count,
        "product_per_user": product_per_user
    }

