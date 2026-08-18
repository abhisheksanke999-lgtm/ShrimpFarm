from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

# =====================================
# Paths
# =====================================

MORTALITY_DIR = Path(__file__).resolve().parent

model = joblib.load(MORTALITY_DIR / "model.pkl")
water_encoder = joblib.load(MORTALITY_DIR / "water_encoder.pkl")
disease_encoder = joblib.load(MORTALITY_DIR / "disease_encoder.pkl")
mortality_encoder = joblib.load(MORTALITY_DIR / "encoder.pkl")


def predict_mortality(
    doc,
    temperature,
    ph,
    dissolved_oxygen,
    salinity,
    water_quality,
    disease_risk,
    recommended_feed,
    previous_mortality,
):

    water_quality = water_encoder.transform([water_quality])[0]
    disease_risk = disease_encoder.transform([disease_risk])[0]

    row = pd.DataFrame(
        [[
            doc,
            temperature,
            ph,
            dissolved_oxygen,
            salinity,
            water_quality,
            disease_risk,
            recommended_feed,
            previous_mortality,
        ]],
        columns=[
            "doc",
            "temperature",
            "ph",
            "dissolved_oxygen",
            "salinity",
            "water_quality",
            "disease_risk",
            "recommended_feed",
            "previous_mortality",
        ],
    )

    prediction = model.predict(row)[0]

    risk = mortality_encoder.inverse_transform([prediction])[0]

    if risk == "Low":
        recommendations = [
            "Continue normal pond management.",
            "Maintain feeding schedule.",
            "Monitor water quality daily.",
        ]

    elif risk == "Medium":
        recommendations = [
            "Increase dissolved oxygen monitoring.",
            "Reduce feeding slightly.",
            "Observe shrimp activity closely.",
        ]

    else:
        recommendations = [
            "High mortality risk detected.",
            "Increase aeration immediately.",
            "Inspect shrimp for disease.",
            "Perform partial water exchange.",
        ]

    return {
        "mortality_risk": risk,
        "recommendations": recommendations,
    }


if __name__ == "__main__":

    result = predict_mortality(
        doc=60,
        temperature=31,
        ph=7.8,
        dissolved_oxygen=3.5,
        salinity=20,
        water_quality="Poor",
        disease_risk="High",
        recommended_feed=180,
        previous_mortality=15,
    )

    print(result)