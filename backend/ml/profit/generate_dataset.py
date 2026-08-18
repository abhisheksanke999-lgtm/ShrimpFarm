import random
from pathlib import Path

import pandas as pd

random.seed(42)

rows = []

for _ in range(10000):

    harvest_weight = round(random.uniform(1000, 7000), 2)

    market_price = random.randint(300, 600)

    feed_cost = random.randint(50000, 300000)

    seed_cost = random.randint(30000, 120000)

    medicine_cost = random.randint(5000, 50000)

    electricity_cost = random.randint(10000, 60000)

    labour_cost = random.randint(15000, 80000)

    other_expenses = random.randint(5000, 40000)

    survival_rate = round(random.uniform(60, 98), 2)

    revenue = harvest_weight * market_price

    total_cost = (
        feed_cost
        + seed_cost
        + medicine_cost
        + electricity_cost
        + labour_cost
        + other_expenses
    )

    profit = revenue - total_cost

    rows.append([
        harvest_weight,
        market_price,
        feed_cost,
        seed_cost,
        medicine_cost,
        electricity_cost,
        labour_cost,
        other_expenses,
        survival_rate,
        round(profit, 2),
    ])

df = pd.DataFrame(
    rows,
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
        "profit",
    ],
)

BASE_DIR = Path(__file__).resolve().parents[1]
DATASET_DIR = BASE_DIR / "dataset"
DATASET_DIR.mkdir(exist_ok=True)

df.to_csv(DATASET_DIR / "profit_dataset.csv", index=False)

print("Profit dataset generated successfully.")