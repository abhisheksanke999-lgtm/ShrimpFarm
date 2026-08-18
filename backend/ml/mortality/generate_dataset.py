import random
from pathlib import Path

import pandas as pd

random.seed(42)

rows = []

for _ in range(10000):

    doc = random.randint(1, 120)

    temperature = round(random.uniform(26, 34), 1)

    ph = round(random.uniform(6.8, 9.2), 1)

    do = round(random.uniform(2.5, 8.0), 1)

    salinity = round(random.uniform(5, 35), 1)

    water_quality = random.choice([
        "Good",
        "Moderate",
        "Poor"
    ])

    disease = random.choice([
        "Healthy",
        "Moderate",
        "High"
    ])

    feed = round(random.uniform(20, 300), 2)

    previous_mortality = random.randint(0, 20)

    score = 0

    if water_quality == "Poor":
        score += 2

    elif water_quality == "Moderate":
        score += 1

    if disease == "High":
        score += 2

    elif disease == "Moderate":
        score += 1

    if do < 4:
        score += 1

    if previous_mortality > 10:
        score += 2

    if score <= 1:
        risk = "Low"

    elif score <= 3:
        risk = "Medium"

    else:
        risk = "High"

    rows.append([
        doc,
        temperature,
        ph,
        do,
        salinity,
        water_quality,
        disease,
        feed,
        previous_mortality,
        risk,
    ])

df = pd.DataFrame(
    rows,
    columns=[
        "doc",
        "temperature",
        "ph",
        "dissolved_oxygen",
        "salinity",
        "water_quality",
        "disease_risk",
        "recommended_feed",
        "previous_mortality",
        "mortality_risk",
    ],
)

BASE_DIR = Path(__file__).resolve().parents[1]

dataset_dir = BASE_DIR / "dataset"

dataset_dir.mkdir(exist_ok=True)

df.to_csv(
    dataset_dir / "mortality_dataset.csv",
    index=False,
)

print("Mortality dataset generated successfully.")