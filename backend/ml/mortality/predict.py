from __future__ import annotations

from pathlib import Path

from ml._lazy import load_pkl

MORTALITY_DIR = Path(__file__).resolve().parent


def _model():
    return load_pkl(MORTALITY_DIR, "model.pkl")


def _water_encoder():
    return load_pkl(MORTALITY_DIR, "water_encoder.pkl")


def _disease_encoder():
    return load_pkl(MORTALITY_DIR, "disease_encoder.pkl")


def _mortality_encoder():
    return load_pkl(MORTALITY_DIR, "encoder.pkl")


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
    model = _model()
    water_encoder = _water_encoder()
    disease_encoder = _disease_encoder()
    mortality_encoder = _mortality_encoder()

    wq = water_encoder.transform([water_quality])[0]
    dr = disease_encoder.transform([disease_risk])[0]

    row = [[
        doc,
        temperature,
        ph,
        dissolved_oxygen,
        salinity,
        wq,
        dr,
        recommended_feed,
        previous_mortality,
    ]]

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
