from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import (
    DailyObservation,
    Pond,
    PredictionRecord,
    User,
)

from ml.feed.predict import predict_feed
from ml.mortality.predict import predict_mortality
from ml.harvest.predict import predict_harvest
from ml.profit.predict import predict_profit


router = APIRouter(
    prefix="/api/ml",
    tags=["ml"],
)


# =========================================================
# REQUEST MODEL
# =========================================================

class PredictAllRequest(BaseModel):

    # Pond information
    pond_name: str
    prediction_date: str

    # Feed inputs
    doc: float = 0
    avg_weight: float = 0
    biomass: float = 0
    temperature: float = 0
    dissolved_oxygen: float = 0
    water_quality: str = "Moderate"
    disease_risk: str = "Healthy"
    yesterday_feed: float = 0

    # Mortality inputs
    ph: float = 0
    salinity: float = 0

    # IMPORTANT:
    # We do NOT ask frontend for previous_mortality.
    # Backend gets it automatically from DailyObservation.

    # Harvest inputs
    survival_rate: float = 0
    fcr: float = 0

    # Profit inputs
    market_price: float = 0
    feed_cost: float = 0
    seed_cost: float = 0
    medicine_cost: float = 0
    electricity_cost: float = 0
    labour_cost: float = 0
    other_expenses: float = 0


# =========================================================
# PREDICT ALL
# =========================================================

@router.post("/predict-all")
@router.post("/predict-all/")
@router.post("/predict")
@router.post("/predict/")
def predict_all(
    payload: PredictAllRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):

    # =====================================================
    # 1. VALIDATE POND
    # =====================================================

    pond_name = payload.pond_name.strip()

    if not pond_name:
        raise HTTPException(
            status_code=400,
            detail="Pond name is required.",
        )

    pond = (
        db.query(Pond)
        .filter(
            Pond.user_id == user.id,
            func.lower(func.trim(Pond.name)) == pond_name.lower(),
        )
        .first()
    )

    if not pond:
        # Check if user has observations for this pond
        obs = (
            db.query(DailyObservation)
            .filter(
                DailyObservation.user_id == user.id,
                func.lower(func.trim(DailyObservation.pond_name)) == pond_name.lower(),
            )
            .first()
        )
        if not obs:
            raise HTTPException(
                status_code=400,
                detail="Invalid pond selected.",
            )
        pond_name = obs.pond_name
    else:
        pond_name = pond.name

    # =====================================================
    # 2. GET PREVIOUS MORTALITY AUTOMATICALLY
    # =====================================================

    try:
        prediction_date = date.fromisoformat(str(payload.prediction_date).strip())
    except (ValueError, TypeError, AttributeError):
        prediction_date = date.today()

    previous_observation = (
        db.query(DailyObservation)
        .filter(
            DailyObservation.user_id == user.id,
            func.lower(DailyObservation.pond_name) == pond_name.lower(),
            DailyObservation.log_date < prediction_date,
        )
        .order_by(
            DailyObservation.log_date.desc(),
            DailyObservation.log_id.desc(),
        )
        .first()
    )

    previous_mortality = (
        float(previous_observation.mortality_count)
        if previous_observation and previous_observation.mortality_count is not None
        else 0
    )

    # Normalize categorical inputs
    wq_input = (payload.water_quality or "").strip().title()
    if wq_input in ("Good", "Moderate", "Poor"):
        water_quality = wq_input
    elif "good" in wq_input.lower():
        water_quality = "Good"
    elif "poor" in wq_input.lower():
        water_quality = "Poor"
    else:
        water_quality = "Moderate"

    dr_input = (payload.disease_risk or "").strip().title()
    if dr_input in ("Healthy", "Moderate", "High"):
        disease_risk = dr_input
    elif "low" in dr_input.lower() or "health" in dr_input.lower():
        disease_risk = "Healthy"
    elif "mod" in dr_input.lower():
        disease_risk = "Moderate"
    elif "high" in dr_input.lower():
        disease_risk = "High"
    else:
        disease_risk = "Healthy"

    # =====================================================
    # 3. GET DISEASE CONFIDENCE FROM DAILY PREDICTION
    # =====================================================

    disease_record = (
        db.query(PredictionRecord)
        .filter(
            PredictionRecord.user_id == user.id,
            func.lower(PredictionRecord.pond_name) == pond_name.lower(),
            PredictionRecord.disease_confidence.isnot(None),
        )
        .order_by(
            PredictionRecord.prediction_id.desc()
        )
        .first()
    )

    disease_confidence = (
        float(disease_record.disease_confidence)
        if disease_record and disease_record.disease_confidence is not None
        else 0
    )

    # =====================================================
    # 4. FEED PREDICTION
    # =====================================================

    try:

        feed_prediction = predict_feed(
            doc=payload.doc,
            avg_weight=payload.avg_weight,
            biomass=payload.biomass,
            temperature=payload.temperature,
            dissolved_oxygen=payload.dissolved_oxygen,
            water_quality=water_quality,
            disease_risk=disease_risk,
            yesterday_feed=payload.yesterday_feed,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Feed prediction failed: {exc}",
        ) from exc

    # =====================================================
    # 5. MORTALITY PREDICTION
    # =====================================================

    try:

        mortality_prediction = predict_mortality(
            doc=payload.doc,
            temperature=payload.temperature,
            ph=payload.ph,
            dissolved_oxygen=payload.dissolved_oxygen,
            salinity=payload.salinity,
            water_quality=water_quality,
            disease_risk=disease_risk,
            recommended_feed=feed_prediction["recommended_feed"],
            previous_mortality=previous_mortality,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Mortality prediction failed: {exc}",
        ) from exc

    # =====================================================
    # 6. HARVEST PREDICTION
    # =====================================================

    try:

        harvest_prediction = predict_harvest(
            doc=payload.doc,
            avg_weight=payload.avg_weight,
            biomass=payload.biomass,
            survival_rate=payload.survival_rate,
            fcr=payload.fcr,
            water_quality=water_quality,
            disease_risk=disease_risk,
            mortality_risk=mortality_prediction[
                "mortality_risk"
            ],
            recommended_feed=feed_prediction[
                "recommended_feed"
            ],
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Harvest prediction failed: {exc}",
        ) from exc

    # =====================================================
    # 7. PROFIT PREDICTION
    # =====================================================

    try:

        profit_prediction = predict_profit(
            harvest_weight=harvest_prediction[
                "expected_harvest_weight"
            ],
            market_price=payload.market_price,
            feed_cost=payload.feed_cost,
            seed_cost=payload.seed_cost,
            medicine_cost=payload.medicine_cost,
            electricity_cost=payload.electricity_cost,
            labour_cost=payload.labour_cost,
            other_expenses=payload.other_expenses,
            survival_rate=payload.survival_rate,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Profit prediction failed: {exc}",
        ) from exc

    # =====================================================
    # 8. SAVE ALL PREDICTIONS
    # =====================================================

    try:

        prediction_row = PredictionRecord(
            user_id=user.id,
            pond_name=pond_name,
            prediction_date=prediction_date,

            water_quality=water_quality,

            disease_risk=disease_risk,

            # Preserve disease confidence
            disease_confidence=disease_confidence,

            recommended_feed=feed_prediction[
                "recommended_feed"
            ],

            mortality_risk=mortality_prediction[
                "mortality_risk"
            ],

            expected_harvest_weight=harvest_prediction[
                "expected_harvest_weight"
            ],

            expected_profit=profit_prediction[
                "expected_profit"
            ],

            alerts="\n".join(
                mortality_prediction.get(
                    "recommendations",
                    []
                )
            ),
        )

        db.add(prediction_row)
        db.commit()
        db.refresh(prediction_row)

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Could not save prediction: {exc}",
        ) from exc

    # =====================================================
    # 9. RETURN ALL RESULTS
    # =====================================================

    return {

        "message":
            "All predictions generated successfully.",

        "previous_mortality":
            previous_mortality,

        "disease_confidence":
            disease_confidence,

        "feed": {

            "recommended_feed":
                feed_prediction[
                    "recommended_feed"
                ],

            "message":
                feed_prediction.get(
                    "message",
                    ""
                ),
        },

        "mortality": {

            "mortality_risk":
                mortality_prediction[
                    "mortality_risk"
                ],

            "recommendations":
                mortality_prediction.get(
                    "recommendations",
                    []
                ),
        },

        "harvest": {

            "expected_harvest_weight":
                harvest_prediction[
                    "expected_harvest_weight"
                ],

            "unit":
                harvest_prediction[
                    "unit"
                ],
        },

        "profit": {

            "expected_profit":
                profit_prediction[
                    "expected_profit"
                ],

            "currency":
                profit_prediction[
                    "currency"
                ],
        },
    }