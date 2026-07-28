from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="Farmer")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    ponds = relationship("Pond", back_populates="owner", cascade="all, delete-orphan")


class Pond(Base):
    __tablename__ = "ponds"

    pond_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    area_sqm: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    depth_m: Mapped[Decimal] = mapped_column(Numeric(4, 2), nullable=False)
    water_source: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="Active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="ponds")


class DailyObservation(Base):
    __tablename__ = "daily_observations"

    log_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    pond_name: Mapped[str] = mapped_column(String(100), nullable=False)
    log_date: Mapped[date] = mapped_column(Date, nullable=False)
    temperature: Mapped[Decimal | None] = mapped_column(Numeric(4, 2), nullable=True)
    ph: Mapped[Decimal | None] = mapped_column(Numeric(4, 2), nullable=True)
    salinity: Mapped[Decimal | None] = mapped_column(Numeric(4, 2), nullable=True)
    dissolved_oxygen: Mapped[Decimal | None] = mapped_column(Numeric(4, 2), nullable=True)
    water_color: Mapped[str | None] = mapped_column(String(50), nullable=True)
    mortality_count: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class FeedRecord(Base):
    __tablename__ = "feed_records"

    feed_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    pond_name: Mapped[str] = mapped_column(String(100), nullable=False)
    feed_brand: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity_kg: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    feeding_time: Mapped[str | None] = mapped_column(String(100), nullable=True)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    feed_size: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ExpenseRecord(Base):
    __tablename__ = "expense_records"

    expense_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class HarvestRecord(Base):
    __tablename__ = "harvest_records"

    harvest_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    pond_name: Mapped[str] = mapped_column(String(100), nullable=False)
    harvest_date: Mapped[date] = mapped_column(Date, nullable=False)
    quantity_kg: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    price_per_kg: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    buyer_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
