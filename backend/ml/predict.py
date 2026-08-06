import joblib
import pandas as pd

# Load trained model
model = joblib.load("ml/disease_model.pkl")
water_encoder = joblib.load("ml/water_encoder.pkl")
disease_encoder = joblib.load("ml/disease_encoder.pkl")


def predict_disease(
    temperature,
    ph,
    dissolved_oxygen,
    salinity,
    water_color,
    mortality_count,
):
    # Encode water color
    water_color_encoded = water_encoder.transform([water_color])[0]

    # Create input dataframe
    input_data = pd.DataFrame(
        [
            {
                "temperature": temperature,
                "ph": ph,
                "dissolved_oxygen": dissolved_oxygen,
                "salinity": salinity,
                "water_color": water_color_encoded,
                "mortality_count": mortality_count,
                # Temporary default values
                "feed_given": 100,
                "pond_age": 60,
            }
        ]
    )

    # Predict disease
    prediction = model.predict(input_data)[0]

    # Prediction confidence
    probability = model.predict_proba(input_data).max()

    # Decode prediction
    disease = disease_encoder.inverse_transform([prediction])[0]

    # Recommendations
    if disease == "Healthy":
        recommendations = [
            "Water quality is good.",
            "Continue regular monitoring.",
            "Maintain feeding schedule."
        ]
    elif disease == "Moderate":
        recommendations = [
            "Check dissolved oxygen.",
            "Reduce feed slightly.",
            "Inspect shrimp behavior."
        ]
    else:
        recommendations = [
            "Increase aeration immediately.",
            "Reduce feeding.",
            "Check ammonia level.",
            "Inspect pond for disease symptoms."
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