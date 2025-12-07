from fastapi import FastAPI, Depends
from app.routers import products, users
from app.db.database import engine
from app.db.models import Base
from app.core.auth import outh2_scheme
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="Backend Course", lifespan=lifespan)

@app.get("/debug-jwt")
def debug_jwt(token: str = Depends(outh2_scheme)):
    return {"reciveed_token": token}

app.include_router(products.router)
app.include_router(users.router)