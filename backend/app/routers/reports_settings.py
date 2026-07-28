from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import ExpenseRecord, FeedRecord, HarvestRecord, Pond, User
from app.schemas import MessageOut, ProfileUpdateIn, ReportsOut, UserOut

router = APIRouter(prefix="/api", tags=["reports-settings"])


@router.get("/reports", response_model=ReportsOut)
def reports(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    total_ponds = db.query(func.count(Pond.pond_id)).filter(Pond.user_id == user.id).scalar() or 0
    total_feed_kg = (
        db.query(func.coalesce(func.sum(FeedRecord.quantity_kg), 0))
        .filter(FeedRecord.user_id == user.id)
        .scalar()
    )
    total_expenses = (
        db.query(func.coalesce(func.sum(ExpenseRecord.amount), 0))
        .filter(ExpenseRecord.user_id == user.id)
        .scalar()
    )
    total_revenue = (
        db.query(func.coalesce(func.sum(HarvestRecord.total_amount), 0))
        .filter(HarvestRecord.user_id == user.id)
        .scalar()
    )
    expenses = float(total_expenses or 0)
    revenue = float(total_revenue or 0)
    return {
        "total_ponds": total_ponds,
        "total_feed_kg": float(total_feed_kg or 0),
        "total_expenses": expenses,
        "total_revenue": revenue,
        "net_profit": revenue - expenses,
    }


@router.put("/settings/profile", response_model=MessageOut)
def update_profile(
    payload: ProfileUpdateIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    full_name = payload.full_name.strip()
    if not full_name:
        raise HTTPException(status_code=400, detail="Please enter your full name.")
    user.full_name = full_name
    db.commit()
    return {"message": "Profile updated successfully!"}


@router.get("/settings/me", response_model=UserOut)
def settings_me(user: User = Depends(get_current_user)):
    return user
