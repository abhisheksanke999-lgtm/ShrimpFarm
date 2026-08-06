"""Disease risk prediction using the trained RandomForest model."""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np

ML_DIR = Path(__file__).resolve().parent

model = joblib.load(ML_DIR / "disease_model.pkl")
water_encoder = joblib.load(ML_DIR / "water_encoder.pkl")
disease_encoder = joblib.load(ML_DIR / "disease_encoder.pkl")

KNOWN_WATER_COLORS = list(getattr(water_encoder, "classes_", []))

WATER_COLOR_ALIASES = {
    "goldiesh brown": "Brown",
    "golden brown": "Brown",
    "brownish": "Brown",
    "no color": "Green",
    "clear": "Green",
    "light green": "Light Green",
    "dark green": "Dark Green",
    "black": "Black",
    "green": "Green",
    "brown": "Brown",
}

# Fallback feature order if older model has no feature_names_in_
DEFAULT_FEATURES = [
    "temperature",
    "ph",
    "dissolved_oxygen",
    "salinity",
    "water_color",
    "mortality_count",
    "feed_given",
    "pond_age",
]


def _normalize_water_color(water_color: str) -> str:
    raw = (water_color or "").strip()
    if not raw:
        return "Light Green" if "Light Green" in KNOWN_WATER_COLORS else KNOWN_WATER_COLORS[0]

    if raw in KNOWN_WATER_COLORS:
        return raw

    alias = WATER_COLOR_ALIASES.get(raw.lower())
    if alias and alias in KNOWN_WATER_COLORS:
        return alias

    lower_map = {c.lower(): c for c in KNOWN_WATER_COLORS}
    if raw.lower() in lower_map:
        return lower_map[raw.lower()]

    raise ValueError(
        f"Unknown water color '{water_color}'. "
        f"Allowed: {', '.join(KNOWN_WATER_COLORS)}"
    )


def predict_disease(
    temperature,
    ph,
    dissolved_oxygen,
    salinity,
    water_color,
    mortality_count,
    feed_given: float = 100,
    pond_age: int = 60,
):
    color = _normalize_water_color(str(water_color))
    water_color_encoded = int(water_encoder.transform([color])[0])

    values = {
        "temperature": float(temperature or 0),
        "ph": float(ph or 0),
        "dissolved_oxygen": float(dissolved_oxygen or 0),
        "salinity": float(salinity or 0),
        "water_color": float(water_color_encoded),
        "mortality_count": float(int(mortality_count or 0)),
        "feed_given": float(feed_given if feed_given is not None else 100),
        "pond_age": float(int(pond_age if pond_age is not None else 60)),
    }

    feature_names = list(getattr(model, "feature_names_in_", DEFAULT_FEATURES))
    row = np.array([[values[name] for name in feature_names]], dtype=float)

    prediction = model.predict(row)[0]
    probability = float(model.predict_proba(row).max())
    disease = disease_encoder.inverse_transform([prediction])[0]

    if disease == "Healthy":
        recommendations = [
            "Water quality is good.",
            "Continue regular monitoring.",
            "Maintain feeding schedule.",
        ]
    elif disease == "Moderate":
        recommendations = [
            "Check dissolved oxygen.",
            "Reduce feed slightly.",
            "Inspect shrimp behavior.",
        ]
    else:
        recommendations = [
            "Increase aeration immediately.",
            "Reduce feeding.",
            "Check ammonia level.",
            "Inspect pond for disease symptoms.",
        ]

    return {
        "disease_risk": disease,
        "confidence": float(round(probability * 100, 2)),
        "recommendations": recommendations,
    }


if __name__ == "__main__":
    result = predict_disease(
        temperature=31,
        ph=7.8,
        dissolved_oxygen=3.2,
        salinity=18,
        water_color="Dark Green",
        mortality_count=12,
    )
    print(result)
