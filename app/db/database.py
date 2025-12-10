from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import os
from dotenv import load_dotenv
load_dotenv() 

DATABASE_URL = str(os.getenv("DATABASE_UR"))

engine = create_async_engine(url=DATABASE_URL, echo=True)

SeccionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_db():
    db: AsyncSession = SeccionLocal()
    try:
        yield db
    finally:
        await db.close()

