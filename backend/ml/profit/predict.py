from __future__ import annotations

from pathlib import Path

from ml._lazy import load_pkl

PROFIT_DIR = Path(__file__).resolve().parent


def _model():
    return load_pkl(PROFIT_DIR, "model.pkl")


def predict_profit(
    harvest_weight,
    market_price,
    feed_cost,
    seed_cost,
    medicine_cost,
    electricity_cost,
    labour_cost,
    other_expenses,
    survival_rate,
):
    model = _model()

    row = [[
        harvest_weight,
        market_price,
        feed_cost,
        seed_cost,
        medicine_cost,
        electricity_cost,
        labour_cost,
        other_expenses,
        survival_rate,
    ]]

    prediction = model.predict(row)[0]

    return {
        "expected_profit": round(float(prediction), 2),
        "currency": "INR",
    }
