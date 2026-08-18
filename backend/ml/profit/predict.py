from pathlib import Path

import joblib
import pandas as pd

PROFIT_DIR = Path(__file__).resolve().parent

model = joblib.load(PROFIT_DIR / "model.pkl")


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

    row = pd.DataFrame(
        [[
            harvest_weight,
            market_price,
            feed_cost,
            seed_cost,
            medicine_cost,
            electricity_cost,
            labour_cost,
            other_expenses,
            survival_rate,
        ]],
        columns=[
            "harvest_weight",
            "market_price",
            "feed_cost",
            "seed_cost",
            "medicine_cost",
            "electricity_cost",
            "labour_cost",
            "other_expenses",
            "survival_rate",
        ],
    )

    prediction = model.predict(row)[0]

    return {
        "expected_profit": round(float(prediction), 2),
        "currency": "INR",
    }


if __name__ == "__main__":

    result = predict_profit(
        harvest_weight=4500,
        market_price=420,
        feed_cost=180000,
        seed_cost=70000,
        medicine_cost=15000,
        electricity_cost=25000,
        labour_cost=30000,
        other_expenses=12000,
        survival_rate=90,
    )

    print(result)