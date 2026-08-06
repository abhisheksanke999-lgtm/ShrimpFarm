from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field


class MessageOut(BaseModel):
    message: str

class PredictionOut(BaseModel):
    disease_risk: str
    confidence: float
    recommendations: list[str]


class DailyPredictionResponse(BaseModel):
    message: str
    prediction: PredictionOut


class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str

    model_config = {"from_attributes": True}


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class RegisterIn(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=4, max_length=128)


class RegisterPendingOut(BaseModel):
    message: str
    email: EmailStr
    expires_in: int


class VerifyOtpIn(BaseModel):
    email: EmailStr
    otp_code: str = Field(min_length=4, max_length=12)


class ResendOtpIn(BaseModel):
    email: EmailStr


class ProfileUpdateIn(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)


class PondCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    area_sqm: float = Field(gt=0)
    depth_m: float = Field(gt=0)
    water_source: str = "Borewell"
    status: str = "Active"


class PondOut(BaseModel):
    pond_id: int
    name: str
    area_sqm: Decimal
    depth_m: Decimal
    water_source: str
    status: str

    model_config = {"from_attributes": True}


class DailyCreate(BaseModel):
    pond_name: str = Field(min_length=1)
    log_date: date
    temperature: float = 0
    ph: float = 0
    salinity: float = 0
    dissolved_oxygen: float = 0
    water_color: str = "Light Green"
    mortality_count: int = 0
    notes: str = ""


class DailyOut(BaseModel):
    log_id: int
    pond_name: str
    log_date: date
    temperature: Decimal | None
    ph: Decimal | None
    salinity: Decimal | None
    dissolved_oxygen: Decimal | None
    water_color: str | None
    mortality_count: int
    notes: str | None

    model_config = {"from_attributes": True}


class FeedCreate(BaseModel):
    pond_name: str = Field(min_length=1)
    feed_brand: str = Field(min_length=1)
    quantity_kg: float = Field(gt=0)
    feeding_time: str = "Morning"
    entry_date: date
    feed_size: str = ""


class FeedOut(BaseModel):
    feed_id: int
    pond_name: str
    feed_brand: str
    quantity_kg: Decimal
    feeding_time: str | None
    entry_date: date
    feed_size: str | None

    model_config = {"from_attributes": True}


class ExpenseCreate(BaseModel):
    expense_date: date
    category: str = "Feed"
    description: str = Field(min_length=1)
    amount: float = Field(gt=0)


class ExpenseOut(BaseModel):
    expense_id: int
    expense_date: date
    category: str
    description: str
    amount: Decimal

    model_config = {"from_attributes": True}


class HarvestCreate(BaseModel):
    pond_name: str = Field(min_length=1)
    harvest_date: date
    quantity_kg: float = Field(gt=0)
    price_per_kg: float = Field(gt=0)
    buyer_name: str = ""


class HarvestOut(BaseModel):
    harvest_id: int
    pond_name: str
    harvest_date: date
    quantity_kg: Decimal
    price_per_kg: Decimal
    total_amount: Decimal
    buyer_name: str | None

    model_config = {"from_attributes": True}


class DashboardOut(BaseModel):
    user_name: str
    active_ponds: int
    total_ponds: int
    total_feed_kg: float
    total_expenses: float
    recent_obs: list[DailyOut]
    ponds_list: list[PondOut]


class ReportsOut(BaseModel):
    total_ponds: int
    total_feed_kg: float
    total_expenses: float
    total_revenue: float
    net_profit: float


class ExpenseListOut(BaseModel):
    items: list[ExpenseOut]
    total_amount: float


class HarvestListOut(BaseModel):
    items: list[HarvestOut]
    total_revenue: float


# Easy to extend later
PL_STAGES = ("PL8", "PL10", "PL12", "PL15", "PL20")


class SeedStockingCreate(BaseModel):
    pond_id: int
    pl_stage: str = Field(min_length=1, max_length=20)
    supplier_name: str = Field(min_length=1, max_length=120)
    batch_number: str = Field(min_length=1, max_length=100)
    total_quantity: int = Field(gt=0)
    cost: float = Field(gt=0)
    stocking_date: date


class SeedStockingUpdate(BaseModel):
    pond_id: int
    pl_stage: str = Field(min_length=1, max_length=20)
    supplier_name: str = Field(min_length=1, max_length=120)
    batch_number: str = Field(min_length=1, max_length=100)
    total_quantity: int = Field(gt=0)
    cost: float = Field(gt=0)
    stocking_date: date


class SeedStockingOut(BaseModel):
    id: int
    pond_id: int
    pond_name: str
    pl_stage: str
    supplier_name: str
    batch_number: str
    total_quantity: int
    cost: Decimal
    cost_per_1000: float
    stocking_date: date
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class SeedStockingListOut(BaseModel):
    items: list[SeedStockingOut]
    total_records: int
    total_pl: int
    total_cost: float
    most_recent_date: date | None
