from __future__ import annotations

from pathlib import Path

from ml._lazy import load_pkl

FEED_DIR = Path(__file__).resolve().parent


def _model():
    return load_pkl(FEED_DIR, "model.pkl")


def _water_encoder():
    return load_pkl(FEED_DIR, "water_encoder.pkl")


def _disease_encoder():
    return load_pkl(FEED_DIR, "disease_encoder.pkl")


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
    water_encoder = _water_encoder()
    disease_encoder = _disease_encoder()
    model = _model()

    wq = water_encoder.transform([water_quality])[0]
    dr = disease_encoder.transform([disease_risk])[0]

    row = [[
        doc,
        avg_weight,
        biomass,
        temperature,
        dissolved_oxygen,
        wq,
        dr,
        yesterday_feed,
    ]]

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
