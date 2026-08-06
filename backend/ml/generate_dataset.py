import pandas as pd
import random
import os

NUM_RECORDS = 10000

water_colors = [
    "Green",
    "Light Green",
    "Dark Green",
    "Brown",
    "Black"
]

data = []

for _ in range(NUM_RECORDS):

    temperature = round(random.uniform(24, 35), 1)
    ph = round(random.uniform(6.5, 9.5), 1)
    dissolved_oxygen = round(random.uniform(2, 8), 1)
    salinity = random.randint(5, 35)
    water_color = random.choice(water_colors)
    mortality = random.randint(0, 40)
    feed_given = random.randint(20, 300)
    pond_age = random.randint(1, 150)

    score = 0

    # Temperature
    if temperature > 33 or temperature < 26:
        score += 2
    elif temperature > 31:
        score += 1

    # pH
    if ph < 7 or ph > 9:
        score += 2
    elif ph < 7.5 or ph > 8.5:
        score += 1

    # Dissolved Oxygen
    if dissolved_oxygen < 4:
        score += 3
    elif dissolved_oxygen < 5:
        score += 1

    # Mortality
    if mortality > 15:
        score += 3
    elif mortality > 5:
        score += 1

    # Water Color
    if water_color == "Black":
        score += 3
    elif water_color == "Dark Green":
        score += 2
    elif water_color == "Brown":
        score += 1

    # Disease Label
    if score <= 3:
        disease = "Healthy"
    elif score <= 7:
        disease = "Moderate"
    else:
        disease = "High"

    data.append([
        temperature,
        ph,
        dissolved_oxygen,
        salinity,
        water_color,
        mortality,
        feed_given,
        pond_age,
        disease
    ])

columns = [
    "temperature",
    "ph",
    "dissolved_oxygen",
    "salinity",
    "water_color",
    "mortality_count",
    "feed_given",
    "pond_age",
    "disease_risk"
]

df = pd.DataFrame(data, columns=columns)

# Create dataset folder if it doesn't exist
os.makedirs("ml/dataset", exist_ok=True)

# Save CSV
df.to_csv("ml/dataset/shrimp_disease_dataset.csv", index=False)

print("✅ Dataset Created Successfully!")
print(f"Total Records: {len(df)}")
print(df.head())