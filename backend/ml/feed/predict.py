from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

# ===================================
# Paths
# ===================================

FEED_DIR = Path(__file__).resolve().parent

model = joblib.load(FEED_DIR / "model.pkl")

water_encoder = joblib.load(FEED_DIR / "water_encoder.pkl")

disease_encoder = joblib.load(FEED_DIR / "disease_encoder.pkl")


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

    water_quality = water_encoder.transform([water_quality])[0]
    disease_risk = disease_encoder.transform([disease_risk])[0]

    row = pd.DataFrame(
        [[
            doc,
            avg_weight,
            biomass,
            temperature,
            dissolved_oxygen,
            water_quality,
            disease_risk,
            yesterday_feed,
        ]],
        columns=[
            "doc",
            "avg_weight",
            "biomass",
            "temperature",
            "dissolved_oxygen",
            "water_quality",
            "disease_risk",
            "yesterday_feed",
        ],
    )

    prediction = model.predict(row)[0]

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


if __name__ == "__main__":

    result = predict_feed(
        doc=65,
        avg_weight=18,
        biomass=4200,
        temperature=31,
        dissolved_oxygen=5.5,
        water_quality="Good",
        disease_risk="Healthy",
        yesterday_feed=180,
    )

    print(result)