from __future__ import annotations

from pathlib import Path

from ml._forest import load_forest

FEED_DIR = Path(__file__).resolve().parent


def predict_feed(
    doc,
    avg_weight,
    biomass,
    temperature,
    dissolved_oxygen,
    water_quality,
    disease_risk,
    yesterday_feed,
):
    model = load_forest(FEED_DIR)

    wq = model.encode("water_quality", water_quality)
    dr = model.encode("disease_risk", disease_risk)

    row = [
        doc,
        avg_weight,
        biomass,
        temperature,
        dissolved_oxygen,
        wq,
        dr,
        yesterday_feed,
    ]

    prediction = model.predict_value(row)

    if prediction < yesterday_feed:
        message = "Reduce feeding today."
    elif prediction > yesterday_feed:
        message = "Increase feeding today."
    else:
        message = "Continue normal feeding."

    return {
        "recommended_feed": round(float(prediction), 2),
        "message": message,
    }
