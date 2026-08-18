from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

PROFIT_DIR = Path(__file__).resolve().parent
ML_DIR = PROFIT_DIR.parent

df = pd.read_csv(ML_DIR / "dataset" / "profit_dataset.csv")

X = df.drop("profit", axis=1)
y = df["profit"]

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

print("R² :", r2_score(y_test, pred))
print("MAE :", mean_absolute_error(y_test, pred))

joblib.dump(model, PROFIT_DIR / "model.pkl")

print("Profit model saved successfully!")