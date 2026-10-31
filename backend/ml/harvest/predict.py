from __future__ import annotations

from pathlib import Path

from ml._lazy import load_pkl

HARVEST_DIR = Path(__file__).resolve().parent


def _model():
    return load_pkl(HARVEST_DIR, "model.pkl")


def _water_encoder():
    return load_pkl(HARVEST_DIR, "water_encoder.pkl")


def _disease_encoder():
    return load_pkl(HARVEST_DIR, "disease_encoder.pkl")


def _mortality_encoder():
    return load_pkl(HARVEST_DIR, "mortality_encoder.pkl")


def predict_harvest(
    doc,
    avg_weight,
    biomass,
    survival_rate,
    fcr,
    water_quality,
    disease_risk,
    mortality_risk,
    recommended_feed,
):
    model = _model()
    water_encoder = _water_encoder()
    disease_encoder = _disease_encoder()
    mortality_encoder = _mortality_encoder()

    row = [[
        doc,
        avg_weight,
        biomass,
        survival_rate,
        fcr,
        water_encoder.transform([water_quality])[0],
        disease_encoder.transform([disease_risk])[0],
        mortality_encoder.transform([mortality_risk])[0],
        recommended_feed,
    ]]

    prediction = model.predict(row)[0]

    return {
        "expected_harvest_weight": round(float(prediction), 2),
        "unit": "kg",
    }
