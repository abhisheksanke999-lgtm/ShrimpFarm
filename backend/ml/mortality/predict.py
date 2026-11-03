from __future__ import annotations

from pathlib import Path

from ml._forest import load_forest

MORTALITY_DIR = Path(__file__).resolve().parent


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
    model = load_forest(MORTALITY_DIR)

    wq = model.encode("water_quality", water_quality)
    dr = model.encode("disease_risk", disease_risk)

    row = [
        doc,
        temperature,
        ph,
        dissolved_oxygen,
        salinity,
        wq,
        dr,
        recommended_feed,
        previous_mortality,
    ]

    risk, _ = model.predict_class(row)

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
