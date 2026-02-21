from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import joblib
import numpy as np
from pydantic import BaseModel
from typing import List
import os

app = FastAPI(
    title="PHQ-9 Mental Health Severity Prediction API",
    description="Optimized Logistic Regression model achieving 98.74% accuracy",
    version="2.0.0",
)

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Load the OPTIMIZED model pipeline (98.74% accuracy)
# ============================================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

model = joblib.load(os.path.join(BASE_DIR, "phq9_severity_model_optimized.joblib"))
metadata = joblib.load(os.path.join(BASE_DIR, "phq9_model_metadata_optimized.joblib"))
scaler = joblib.load(os.path.join(BASE_DIR, "phq9_scaler_optimized.joblib"))
selector = joblib.load(os.path.join(BASE_DIR, "phq9_feature_selector.joblib"))
poly = joblib.load(os.path.join(BASE_DIR, "phq9_poly_generator.joblib"))

SEVERITY_LABELS = ["Minimal", "Mild", "Moderate", "Moderately Severe", "Severe"]

# ============================================================================
# Mappings (must match exactly what the model was trained on)
# ============================================================================
GENDER_MAP = {"Male": 0, "Female": 1}
SLEEP_MAP = {"Good": 0, "Average": 1, "Bad": 2, "Worst": 3}
PRESSURE_MAP = {"Good": 0, "Average": 1, "Bad": 2, "Worst": 3}


# ============================================================================
# Request / Response schemas
# ============================================================================
class PHQ9Input(BaseModel):
    age: int
    gender: str                # "Male" or "Female"
    phq9: List[int]            # exactly 9 values, each 0-3
    sleep_quality: str         # "Good", "Average", "Bad", "Worst"
    study_pressure: str        # "Good", "Average", "Bad", "Worst"
    financial_pressure: str    # "Good", "Average", "Bad", "Worst"


class PredictionResponse(BaseModel):
    severity_code: int
    severity_label: str
    confidence: float
    probabilities: dict
    model_accuracy: str


# ============================================================================
# Endpoints
# ============================================================================
@app.post("/predict", response_model=PredictionResponse)
def predict_phq9(input: PHQ9Input):
    """
    Predict PHQ-9 mental health severity using the optimized model.

    Pipeline: raw features → engineered aggregates → polynomial interactions
              → standard scaling → feature selection → logistic regression
    """
    # 1. Map categorical inputs to numeric values
    gender = GENDER_MAP.get(input.gender, 0)
    sleep = SLEEP_MAP.get(input.sleep_quality, 1)
    study = PRESSURE_MAP.get(input.study_pressure, 1)
    financial = PRESSURE_MAP.get(input.financial_pressure, 1)

    # 2. Build base feature vector (14 features = Age, Gender, 9 PHQ items, Sleep, Study, Financial)
    base_features = [
        input.age,
        gender,
        *input.phq9,      # 9 symptom scores (0-3 each)
        sleep,
        study,
        financial,
    ]

    # 3. Engineer the same aggregate features used during training
    symptom_subtotal_1 = sum(input.phq9[0:4])   # first 4 symptoms
    symptom_subtotal_2 = sum(input.phq9[4:9])   # last 5 symptoms
    stress_score = study + financial + sleep

    all_features = base_features + [symptom_subtotal_1, symptom_subtotal_2, stress_score]

    # 4. Full pipeline: poly → scale → select → predict
    data = np.array(all_features).reshape(1, -1)
    data_poly = poly.transform(data)
    data_scaled = scaler.transform(data_poly)
    data_selected = selector.transform(data_scaled)

    prediction = model.predict(data_selected)
    probabilities = model.predict_proba(data_selected)

    severity_code = int(prediction[0])
    severity_label = SEVERITY_LABELS[severity_code]
    confidence = float(np.max(probabilities[0]))

    prob_dict = {
        SEVERITY_LABELS[i]: round(float(probabilities[0][i]), 4)
        for i in range(len(SEVERITY_LABELS))
    }

    return PredictionResponse(
        severity_code=severity_code,
        severity_label=severity_label,
        confidence=round(confidence, 4),
        probabilities=prob_dict,
        model_accuracy="98.74%",
    )


@app.get("/")
def root():
    return {
        "message": "PHQ-9 Optimized Model API is running",
        "model": "Logistic Regression (Optimized)",
        "accuracy": "98.74%",
        "version": "2.0.0",
    }


@app.get("/model-info")
def model_info():
    """Return full model metadata and performance metrics."""
    safe_metadata = {}
    for key, value in metadata.items():
        if isinstance(value, (str, int, float, bool, list)):
            safe_metadata[key] = value
        elif isinstance(value, dict):
            safe_metadata[key] = {
                str(k): (float(v) if isinstance(v, (int, float, np.floating)) else str(v))
                for k, v in value.items()
            }
        else:
            safe_metadata[key] = str(value)
    return safe_metadata
