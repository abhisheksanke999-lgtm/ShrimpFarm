"""Disease risk prediction using the trained RandomForest model."""

from __future__ import annotations

from pathlib import Path

from ml._lazy import load_pkl

DISEASE_DIR = Path(__file__).resolve().parent

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


def _model():
    return load_pkl(DISEASE_DIR, "model.pkl")


def _water_encoder():
    return load_pkl(DISEASE_DIR, "water_encoder.pkl")


def _disease_encoder():
    return load_pkl(DISEASE_DIR, "encoder.pkl")


def _known_water_colors() -> list:
    enc = _water_encoder()
    return list(getattr(enc, "classes_", []))


def _normalize_water_color(water_color: str) -> str:
    known = _known_water_colors()
    raw = (water_color or "").strip()

    if not raw:
        return "Light Green" if "Light Green" in known else known[0]

    if raw in known:
        return raw

    alias = WATER_COLOR_ALIASES.get(raw.lower())
    if alias and alias in known:
        return alias

    lower_map = {c.lower(): c for c in known}
    if raw.lower() in lower_map:
        return lower_map[raw.lower()]

    raise ValueError(
        f"Unknown water color '{water_color}'. Allowed: {', '.join(known)}"
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
    model = _model()
    water_encoder = _water_encoder()
    disease_encoder = _disease_encoder()

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
    row = [[values[name] for name in feature_names]]

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
        "confidence": round(probability * 100, 2),
        "recommendations": recommendations,
    }
