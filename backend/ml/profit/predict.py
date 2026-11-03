from __future__ import annotations

from pathlib import Path

from ml._forest import load_forest

PROFIT_DIR = Path(__file__).resolve().parent


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
    model = load_forest(PROFIT_DIR)

    row = [
        harvest_weight,
        market_price,
        feed_cost,
        seed_cost,
        medicine_cost,
        electricity_cost,
        labour_cost,
        other_expenses,
        survival_rate,
    ]

    prediction = model.predict_value(row)

    return {
        "expected_profit": round(float(prediction), 2),
        "currency": "INR",
    }
