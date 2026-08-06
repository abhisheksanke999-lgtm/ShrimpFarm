import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# ==============================
# Load Dataset
# ==============================

df = pd.read_csv("ml/dataset/shrimp_disease_dataset.csv")

print("Dataset Loaded Successfully!")
print(df.head())

# ==============================
# Encode Categorical Features
# ==============================

water_encoder = LabelEncoder()
df["water_color"] = water_encoder.fit_transform(df["water_color"])

disease_encoder = LabelEncoder()
df["disease_risk"] = disease_encoder.fit_transform(df["disease_risk"])

# ==============================
# Split Features and Target
# ==============================

X = df.drop("disease_risk", axis=1)
y = df["disease_risk"]

# ==============================
# Train-Test Split
# ==============================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# ==============================
# Train Model
# ==============================

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

model.fit(X_train, y_train)

# ==============================
# Prediction
# ==============================

y_pred = model.predict(X_test)

# ==============================
# Evaluation
# ==============================

accuracy = accuracy_score(y_test, y_pred)

print("\n==============================")
print("MODEL ACCURACY")
print("==============================")
print(f"{accuracy*100:.2f}%")

print("\nClassification Report\n")
print(classification_report(y_test, y_pred))

print("\nConfusion Matrix\n")
print(confusion_matrix(y_test, y_pred))

# ==============================
# Save Model
# ==============================

joblib.dump(model, "ml/disease_model.pkl")
joblib.dump(water_encoder, "ml/water_encoder.pkl")
joblib.dump(disease_encoder, "ml/disease_encoder.pkl")

print("\nModel Saved Successfully!")
