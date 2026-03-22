import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

# Expecting a PostgreSQL URL like: postgresql+asyncpg://user:password@host/dbname
# E.g., from Neon or Supabase
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)
Base = declarative_base()

# We will define our Caching Models here later (e.g. HotelCache, ReviewCache)
# format:
# class HotelCache(Base):
#     __tablename__ = "hotel_cache"
#     id = Column(Integer, primary_key=True, index=True)
#     ...

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
