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

from sqlalchemy import Column, Integer, String, Boolean, DateTime
import datetime

# We will define our Caching Models here later (e.g. HotelCache, ReviewCache)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=True) # allow null during raw OTP creation
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True) # allow null since moving to OTP
    is_active = Column(Boolean, default=True)

    # --- NEW OTP COLUMNS ADDED BY AKANSH SAXENA ---
    otp = Column(String, nullable=True)
    otp_expiry = Column(DateTime, nullable=True)

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True, nullable=False)
    hotel_name = Column(String, nullable=False)
    amount_inr = Column(Integer, nullable=False) # Razorpay works in smallest currency unit (paise)
    razorpay_order_id = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, default="PENDING")

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
