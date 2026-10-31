from pathlib import Path

import joblib


HARVEST_DIR = Path(__file__).resolve().parent

model = joblib.load(HARVEST_DIR / "model.pkl")

water_encoder = joblib.load(HARVEST_DIR / "water_encoder.pkl")
disease_encoder = joblib.load(HARVEST_DIR / "disease_encoder.pkl")
mortality_encoder = joblib.load(HARVEST_DIR / "mortality_encoder.pkl")


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

    row = pd.DataFrame(
        [[
            doc,
            avg_weight,
            biomass,
            survival_rate,
            fcr,
            water_encoder.transform([water_quality])[0],
            disease_encoder.transform([disease_risk])[0],
            mortality_encoder.transform([mortality_risk])[0],
            recommended_feed,
        ]],
        columns=[
            "doc",
            "avg_weight",
            "biomass",
            "survival_rate",
            "fcr",
            "water_quality",
            "disease_risk",
            "mortality_risk",
            "recommended_feed",
        ],
    )

    prediction = model.predict(row)[0]

    return {
        "expected_harvest_weight": round(float(prediction), 2),
        "unit": "kg"
    }


if __name__ == "__main__":

    result = predict_harvest(
        doc=110,
        avg_weight=28,
        biomass=6200,
        survival_rate=88,
        fcr=1.4,
        water_quality="Good",
        disease_risk="Healthy",
        mortality_risk="Low",
        recommended_feed=220,
    )

    print(result)