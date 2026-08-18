from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
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


class PendingRegistration(Base):
    """Signup waiting for email OTP verification (RentYaar-style)."""

    __tablename__ = "pending_registrations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    otp_code: Mapped[str] = mapped_column(String(12), nullable=False)
    otp_expiry: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


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
    seed_stockings = relationship("SeedStocking", back_populates="pond", cascade="all, delete-orphan")


class SeedStocking(Base):
    __tablename__ = "seed_stocking"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "supplier_name",
            "batch_number",
            name="uq_seed_stocking_user_supplier_batch",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    pond_id: Mapped[int] = mapped_column(ForeignKey("ponds.pond_id", ondelete="CASCADE"), nullable=False, index=True)
    pl_stage: Mapped[str] = mapped_column(String(20), nullable=False)
    supplier_name: Mapped[str] = mapped_column(String(120), nullable=False)
    batch_number: Mapped[str] = mapped_column(String(100), nullable=False)
    total_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    stocking_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    pond = relationship("Pond", back_populates="seed_stockings")

class DailyObservation(Base):
    __tablename__ = "daily_observations"

    log_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    pond_name: Mapped[str] = mapped_column(String(100), nullable=False)

    log_date: Mapped[date] = mapped_column(Date, nullable=False)

    # ==========================
    # Water Quality
    # ==========================

    temperature: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    ph: Mapped[Decimal | None] = mapped_column(Numeric(4, 2))
    salinity: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    dissolved_oxygen: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    water_color: Mapped[str | None] = mapped_column(String(50))

    # ==========================
    # Disease
    # ==========================

    mortality_count: Mapped[int] = mapped_column(Integer, default=0)

    # ==========================
    # Feed Prediction Inputs
    # ==========================

    doc: Mapped[int] = mapped_column(Integer, default=0)

    avg_weight: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))

    biomass: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))

    yesterday_feed: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    # ==========================
    # Harvest Inputs
    # ==========================

    survival_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))

    fcr: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))

    # ==========================
    # Profit Inputs
    # ==========================

    market_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    feed_cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))

    seed_cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))

    medicine_cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))

    electricity_cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))

    labour_cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))

    other_expenses: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))

    # ==========================
    # Notes
    # ==========================

    notes: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


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


class PredictionRecord(Base):
    __tablename__ = "prediction_records"

    prediction_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    pond_name: Mapped[str] = mapped_column(String(100), nullable=False)

    prediction_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    water_quality: Mapped[str | None] = mapped_column(String(50))

    disease_risk: Mapped[str | None] = mapped_column(String(50))

    disease_confidence: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2)
    )

    recommended_feed: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2)
    )

    mortality_risk: Mapped[str | None] = mapped_column(String(50))

    expected_harvest_weight: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2)
    )

    expected_profit: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2)
    )

    alerts: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )