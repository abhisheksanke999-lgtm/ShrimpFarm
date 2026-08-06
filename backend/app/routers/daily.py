from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import DailyObservation, Pond, User
from app.schemas import DailyCreate, DailyOut, DailyPredictionResponse

from ml.predict import predict_disease

router = APIRouter(prefix="/api/daily", tags=["daily"])


def _own_pond(db: Session, user_id: int, pond_name: str) -> bool:
    print("Logged-in User ID:", user_id)
    print("Pond Name:", pond_name)

    pond = (
        db.query(Pond)
        .filter(
            Pond.user_id == user_id,
            Pond.name == pond_name
        )
        .first()
    )

    print("Database Result:", pond)

    return pond is not None


@router.get("", response_model=list[DailyOut])
def list_daily(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return (
        db.query(DailyObservation)
        .filter(DailyObservation.user_id == user.id)
        .order_by(
            DailyObservation.log_date.desc(),
            DailyObservation.log_id.desc(),
        )
        .all()
    )


@router.post("", response_model=DailyPredictionResponse)
def create_daily(
    payload: DailyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    pond_name = payload.pond_name.strip()

    if not pond_name or not payload.log_date:
        raise HTTPException(
            status_code=400,
            detail="Please select a pond and date."
        )

    if not _own_pond(db, user.id, pond_name):
        raise HTTPException(
            status_code=400,
            detail="Invalid pond selected."
        )

    row = DailyObservation(
        user_id=user.id,
        pond_name=pond_name,
        log_date=payload.log_date,
        temperature=payload.temperature,
        ph=payload.ph,
        salinity=payload.salinity,
        dissolved_oxygen=payload.dissolved_oxygen,
        water_color=payload.water_color or "Light Green",
        mortality_count=payload.mortality_count or 0,
        notes=payload.notes.strip() if payload.notes else None,
    )

    prediction = predict_disease(
        temperature=payload.temperature,
        ph=payload.ph,
        dissolved_oxygen=payload.dissolved_oxygen,
        salinity=payload.salinity,
        water_color=payload.water_color or "Light Green",
        mortality_count=payload.mortality_count or 0,
    )

    db.add(row)
    db.commit()

    return {
        "message": "Daily log saved successfully!",
        "prediction": prediction,
    }