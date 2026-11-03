from __future__ import annotations

from pathlib import Path

from ml._forest import load_forest

HARVEST_DIR = Path(__file__).resolve().parent


def predict_harvest(
    doc,
    avg_weight,
    biomass,
    survival_rate,
    fcr,
    water_quality,
    disease_risk,
    mortality_risk,
    recommended_feed,
):
    model = load_forest(HARVEST_DIR)

    row = [
        doc,
        avg_weight,
        biomass,
        survival_rate,
        fcr,
        model.encode("water_quality", water_quality),
        model.encode("disease_risk", disease_risk),
        model.encode("mortality_risk", mortality_risk),
        recommended_feed,
    ]

    prediction = model.predict_value(row)

    return {
        "expected_harvest_weight": round(float(prediction), 2),
        "unit": "kg",
    }
