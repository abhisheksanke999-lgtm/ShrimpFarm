from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# ===========================
# Paths
# ===========================

MORTALITY_DIR = Path(__file__).resolve().parent
ML_DIR = MORTALITY_DIR.parent

DATASET_PATH = ML_DIR / "dataset" / "mortality_dataset.csv"

# ===========================
# Load Dataset
# ===========================

df = pd.read_csv(DATASET_PATH)

print(df.head())

# ===========================
# Encoding
# ===========================

water_encoder = LabelEncoder()
df["water_quality"] = water_encoder.fit_transform(df["water_quality"])

disease_encoder = LabelEncoder()
df["disease_risk"] = disease_encoder.fit_transform(df["disease_risk"])

mortality_encoder = LabelEncoder()
df["mortality_risk"] = mortality_encoder.fit_transform(df["mortality_risk"])

# ===========================
# Split
# ===========================

X = df.drop("mortality_risk", axis=1)
y = df["mortality_risk"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)

# ===========================
# Train Model
# ===========================

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
)

model.fit(X_train, y_train)

# ===========================
# Evaluation
# ===========================

pred = model.predict(X_test)

print("\nAccuracy :", accuracy_score(y_test, pred))

print("\nClassification Report\n")
print(classification_report(y_test, pred))

# ===========================
# Save
# ===========================

joblib.dump(model, MORTALITY_DIR / "model.pkl")
joblib.dump(water_encoder, MORTALITY_DIR / "water_encoder.pkl")
joblib.dump(disease_encoder, MORTALITY_DIR / "disease_encoder.pkl")
joblib.dump(mortality_encoder, MORTALITY_DIR / "encoder.pkl")

print("\nMortality model saved successfully!")