from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import (
    DailyObservation,
    ExpenseRecord,
    FeedRecord,
    Pond,
    PredictionRecord,
    User,
)
from app.schemas import DashboardOut

router = APIRouter(
    prefix="/api/dashboard",
    tags=["dashboard"]
)


@router.get("", response_model=DashboardOut)
def dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):

    # =====================================================
    # POND COUNTS
    # =====================================================

    total_ponds = (
        db.query(func.count(Pond.pond_id))
        .filter(Pond.user_id == user.id)
        .scalar()
        or 0
    )

    active_ponds = (
        db.query(func.count(Pond.pond_id))
        .filter(
            Pond.user_id == user.id,
            Pond.status == "Active"
        )
        .scalar()
        or 0
    )

    # =====================================================
    # FEED
    # =====================================================

    total_feed_kg = (
        db.query(
            func.coalesce(
                func.sum(FeedRecord.quantity_kg),
                0
            )
        )
        .filter(
            FeedRecord.user_id == user.id
        )
        .scalar()
    )

    # =====================================================
    # EXPENSES
    # =====================================================

    total_expenses = (
        db.query(
            func.coalesce(
                func.sum(ExpenseRecord.amount),
                0
            )
        )
        .filter(
            ExpenseRecord.user_id == user.id
        )
        .scalar()
    )

    # =====================================================
    # RECENT DAILY OBSERVATIONS
    # =====================================================

    recent_obs = (
        db.query(DailyObservation)
        .filter(
            DailyObservation.user_id == user.id
        )
        .order_by(
            DailyObservation.log_date.desc(),
            DailyObservation.log_id.desc()
        )
        .limit(5)
        .all()
    )

    # =====================================================
    # USER'S PONDS
    # =====================================================

    ponds_list = (
        db.query(Pond)
        .filter(
            Pond.user_id == user.id
        )
        .order_by(
            Pond.pond_id.asc()
        )
        .limit(5)
        .all()
    )

    # =====================================================
    # LATEST AI PREDICTION
    # =====================================================

    latest_prediction = (
        db.query(PredictionRecord)
        .filter(
            PredictionRecord.user_id == user.id
        )
        .order_by(
            PredictionRecord.prediction_id.desc()
        )
        .first()
    )

    # =====================================================
    # RETURN DASHBOARD DATA
    # =====================================================

    return {
        "user_name": user.full_name,

        "active_ponds": active_ponds,
        "total_ponds": total_ponds,

        "total_feed_kg": float(
            total_feed_kg or 0
        ),

        "total_expenses": float(
            total_expenses or 0
        ),

        "recent_obs": recent_obs,

        "ponds_list": ponds_list,

        "latest_prediction": latest_prediction,
    }