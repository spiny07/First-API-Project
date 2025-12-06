from fastapi import FastAPI
from app.routers import products, users
from app.db.database import engine
from app.db.models import Base

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="Backend Course", lifespan=lifespan)

app.include_router(products.router)
app.include_router(users.router)
