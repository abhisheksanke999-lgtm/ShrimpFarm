import random
from pathlib import Path

import pandas as pd

random.seed(42)

rows = []

for _ in range(10000):

    doc = random.randint(60, 140)

    avg_weight = round(random.uniform(8, 40), 2)

    biomass = round(random.uniform(1000, 8000), 2)

    survival_rate = round(random.uniform(60, 98), 2)

    fcr = round(random.uniform(1.0, 2.2), 2)

    water_quality = random.choice(
        ["Good", "Moderate", "Poor"]
    )

    disease_risk = random.choice(
        ["Healthy", "Moderate", "High"]
    )

    mortality_risk = random.choice(
        ["Low", "Medium", "High"]
    )

    feed = round(random.uniform(50, 350), 2)

    harvest_weight = (
        biomass *
        (survival_rate / 100) *
        (1 / fcr)
    )

    if water_quality == "Poor":
        harvest_weight *= 0.90

    if disease_risk == "High":
        harvest_weight *= 0.85

    if mortality_risk == "High":
        harvest_weight *= 0.80

    harvest_weight = round(harvest_weight, 2)

    rows.append([
        doc,
        avg_weight,
        biomass,
        survival_rate,
        fcr,
        water_quality,
        disease_risk,
        mortality_risk,
        feed,
        harvest_weight,
    ])

df = pd.DataFrame(
    rows,
    columns=[
        "doc",
        "avg_weight",
        "biomass",
        "survival_rate",
        "fcr",
        "water_quality",
        "disease_risk",
        "mortality_risk",
        "recommended_feed",
        "harvest_weight",
    ],
)

BASE_DIR = Path(__file__).resolve().parents[1]
DATASET_DIR = BASE_DIR / "dataset"

DATASET_DIR.mkdir(exist_ok=True)

df.to_csv(
    DATASET_DIR / "harvest_dataset.csv",
    index=False,
)

print("Harvest dataset generated successfully.")