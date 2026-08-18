import random
from pathlib import Path

import pandas as pd

random.seed(42)

rows = []

for _ in range(10000):

    doc = random.randint(1, 120)
    avg_weight = round(random.uniform(0.2, 35), 2)
    biomass = round(random.uniform(100, 7000), 2)
    temperature = round(random.uniform(26, 34), 1)
    dissolved_oxygen = round(random.uniform(2.5, 8.0), 1)

    water_quality = random.choice(
        ["Good", "Moderate", "Poor"]
    )

    disease_risk = random.choice(
        ["Healthy", "Moderate", "High"]
    )

    yesterday_feed = round(random.uniform(20, 300), 2)

    feed = yesterday_feed

    if water_quality == "Poor":
        feed *= 0.85
    elif water_quality == "Moderate":
        feed *= 0.95

    if disease_risk == "High":
        feed *= 0.80
    elif disease_risk == "Moderate":
        feed *= 0.90

    if dissolved_oxygen < 4:
        feed *= 0.90

    if temperature > 33:
        feed *= 0.95

    feed = round(feed, 2)

    rows.append([
        doc,
        avg_weight,
        biomass,
        temperature,
        dissolved_oxygen,
        water_quality,
        disease_risk,
        yesterday_feed,
        feed,
    ])

df = pd.DataFrame(
    rows,
    columns=[
        "doc",
        "avg_weight",
        "biomass",
        "temperature",
        "dissolved_oxygen",
        "water_quality",
        "disease_risk",
        "yesterday_feed",
        "recommended_feed",
    ],
)

BASE_DIR = Path(__file__).resolve().parents[1]
DATASET_DIR = BASE_DIR / "dataset"
DATASET_DIR.mkdir(exist_ok=True)

df.to_csv(
    DATASET_DIR / "feed_dataset.csv",
    index=False,
)

print("Feed dataset generated successfully!")