from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# ============================
# Paths
# ============================

FEED_DIR = Path(__file__).resolve().parent
ML_DIR = FEED_DIR.parent

DATASET_PATH = ML_DIR / "dataset" / "feed_dataset.csv"

# ============================
# Load Dataset
# ============================

df = pd.read_csv(DATASET_PATH)

print(df.head())

# ============================
# Encoding
# ============================

water_encoder = LabelEncoder()
df["water_quality"] = water_encoder.fit_transform(df["water_quality"])

disease_encoder = LabelEncoder()
df["disease_risk"] = disease_encoder.fit_transform(df["disease_risk"])

# ============================
# Split
# ============================

X = df.drop("recommended_feed", axis=1)
y = df["recommended_feed"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
)

# ============================
# Train
# ============================

model = RandomForestRegressor(
    n_estimators=200,
    random_state=42,
)

model.fit(X_train, y_train)

# ============================
# Evaluation
# ============================

pred = model.predict(X_test)

print()

print("R2 Score :", r2_score(y_test, pred))
print("MAE      :", mean_absolute_error(y_test, pred))

# ============================
# Save
# ============================

joblib.dump(model, FEED_DIR / "model.pkl")
joblib.dump(water_encoder, FEED_DIR / "water_encoder.pkl")
joblib.dump(disease_encoder, FEED_DIR / "disease_encoder.pkl")

print("\nFeed model saved successfully!")