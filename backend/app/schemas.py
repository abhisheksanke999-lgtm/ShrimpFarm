from datetime import date
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field


class MessageOut(BaseModel):
    message: str


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
