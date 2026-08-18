from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

HARVEST_DIR = Path(__file__).resolve().parent
ML_DIR = HARVEST_DIR.parent

DATASET = ML_DIR / "dataset" / "harvest_dataset.csv"

df = pd.read_csv(DATASET)

print(df.head())

water_encoder = LabelEncoder()
df["water_quality"] = water_encoder.fit_transform(df["water_quality"])

disease_encoder = LabelEncoder()
df["disease_risk"] = disease_encoder.fit_transform(df["disease_risk"])

mortality_encoder = LabelEncoder()
df["mortality_risk"] = mortality_encoder.fit_transform(df["mortality_risk"])

X = df.drop("harvest_weight", axis=1)
y = df["harvest_weight"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
)

model = RandomForestRegressor(
    n_estimators=200,
    random_state=42,
)

model.fit(X_train, y_train)

pred = model.predict(X_test)

print("\nR2 Score :", r2_score(y_test, pred))
print("MAE :", mean_absolute_error(y_test, pred))

joblib.dump(model, HARVEST_DIR / "model.pkl")
joblib.dump(water_encoder, HARVEST_DIR / "water_encoder.pkl")
joblib.dump(disease_encoder, HARVEST_DIR / "disease_encoder.pkl")
joblib.dump(mortality_encoder, HARVEST_DIR / "mortality_encoder.pkl")

print("\nHarvest model saved successfully!")