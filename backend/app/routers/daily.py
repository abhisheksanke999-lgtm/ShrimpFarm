from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import DailyObservation, Pond, PredictionRecord, User
from app.schemas import DailyCreate, DailyOut, DailyPredictionResponse, MessageOut


router = APIRouter(
    prefix="/api/daily",
    tags=["daily"],
)


# =========================================================
# Check whether the pond belongs to the logged-in user
# =========================================================

def _own_pond(
    db: Session,
    user_id: int,
    pond_name: str,
) -> bool:

    pond = (
        db.query(Pond)
        .filter(
            Pond.user_id == user_id,
            Pond.name == pond_name,
        )
        .first()
    )

    return pond is not None


# =========================================================
# WATER QUALITY CLASSIFICATION
# =========================================================

def get_water_quality(
    temperature,
    ph,
    dissolved_oxygen,
    salinity,
):
    """
    Rule-based water quality classification.
    """

    # Good water quality
    if (
        28 <= temperature <= 32
        and 7.5 <= ph <= 8.5
        and dissolved_oxygen >= 5
        and 10 <= salinity <= 25
    ):
        return "Good"

    # Poor water quality
    if (
        dissolved_oxygen < 3
        or ph < 6.5
        or ph > 9
    ):
        return "Poor"

    # Anything between the above conditions
    return "Moderate"# =========================================================
# GET DAILY OBSERVATIONS
# =========================================================

@router.get(
    "",
    response_model=list[DailyOut],
)
def list_daily(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):

    return (
        db.query(DailyObservation)
        .filter(
            DailyObservation.user_id == user.id
        )
        .order_by(
            DailyObservation.log_date.desc(),
            DailyObservation.log_id.desc(),
        )
        .all()
    )


# =========================================================
# CREATE DAILY OBSERVATION
#
# IMPORTANT:
# Daily Observation calls ONLY disease prediction.
#
# Feed, mortality, harvest and profit will be handled
# separately through the AI prediction workflow.
# =========================================================

@router.post("", response_model=DailyPredictionResponse)
def create_daily(
    payload: DailyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # -------------------------
    # 1. Validate pond
    # -------------------------

    pond_name = payload.pond_name.strip()

    if not pond_name:
        raise HTTPException(
            status_code=400,
            detail="Please select a pond.",
        )

    if not _own_pond(db, user.id, pond_name):
        raise HTTPException(
            status_code=400,
            detail="Invalid pond selected.",
        )

    # -------------------------
    # 2. Prepare water color
    # -------------------------

    water_color = (
        payload.water_color or "Light Green"
    ).strip()

    # -------------------------
    # 3. Calculate water quality
    # -------------------------

    water_quality = get_water_quality(
        temperature=payload.temperature,
        ph=payload.ph,
        dissolved_oxygen=payload.dissolved_oxygen,
        salinity=payload.salinity,
    )

    try:
        # -------------------------
        # 4. Disease prediction ONLY
        # -------------------------
        from ml.disease.predict import predict_disease

        disease_prediction = predict_disease(
            temperature=payload.temperature,
            ph=payload.ph,
            dissolved_oxygen=payload.dissolved_oxygen,
            salinity=payload.salinity,
            water_color=water_color,
            mortality_count=payload.mortality_count,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Disease prediction failed: {str(exc)}",
        )

    # -------------------------
    # 5. Save Daily Observation
    # -------------------------

    row = DailyObservation(
        user_id=user.id,
        pond_name=pond_name,
        log_date=payload.log_date,

        # Water
        temperature=payload.temperature,
        ph=payload.ph,
        salinity=payload.salinity,
        dissolved_oxygen=payload.dissolved_oxygen,
        water_color=water_color,

        # Disease
        mortality_count=payload.mortality_count,

        # Notes
        notes=payload.notes.strip()
        if payload.notes
        else None,
    )

    db.add(row)
    db.commit()
    db.refresh(row)

    # -------------------------
    # 6. Save Disease Prediction
    # -------------------------

    prediction_row = PredictionRecord(
        user_id=user.id,
        pond_name=pond_name,
        prediction_date=payload.log_date,

        water_quality=water_quality,

        disease_risk=disease_prediction["disease_risk"],
        disease_confidence=disease_prediction["confidence"],

        # These are intentionally empty here.
        # They will be generated by /api/ml/predict-all.
        recommended_feed=None,
        mortality_risk=None,
        expected_harvest_weight=None,
        expected_profit=None,

        alerts="\n".join(
            disease_prediction.get(
                "recommendations",
                []
            )
        ),
    )

    db.add(prediction_row)
    db.commit()
    db.refresh(prediction_row)

    # -------------------------
    # 7. Return disease prediction
    # -------------------------

    return {
        "message": "Daily log saved successfully!",
        "prediction": disease_prediction,
    }


@router.delete("/{log_id}", response_model=MessageOut)
def delete_daily(
    log_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = (
        db.query(DailyObservation)
        .filter(
            DailyObservation.log_id == log_id,
            DailyObservation.user_id == user.id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Daily observation not found.")

    db.query(PredictionRecord).filter(
        PredictionRecord.user_id == user.id,
        PredictionRecord.pond_name == row.pond_name,
        PredictionRecord.prediction_date == row.log_date,
        PredictionRecord.recommended_feed.is_(None),
        PredictionRecord.mortality_risk.is_(None),
    ).delete(synchronize_session=False)

    db.delete(row)
    db.commit()
    return {"message": "Daily observation deleted."}