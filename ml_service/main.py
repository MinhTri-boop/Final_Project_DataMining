from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
from pathlib import Path

# Setup Path
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "ml" / "models" / "xgboost_classifier.pkl"

app = FastAPI(
    title="Global Security & Risk Intelligence - ML Service",
    description="Inference API for predicting terrorist attack success probabilities.",
    version="1.0.0"
)

# Load the model globally at startup
model = None
try:
    if MODEL_PATH.exists():
        model = joblib.load(MODEL_PATH)
        print(f"Loaded XGBoost model from {MODEL_PATH}")
    else:
        print(f"Warning: Model not found at {MODEL_PATH}")
except Exception as e:
    print(f"Error loading model: {e}")

class PredictionRequest(BaseModel):
    iyear: int
    region: int
    country: int
    attacktype1: int
    targtype1: int
    weaptype1: int

@app.get("/")
def read_root():
    return {"message": "ML Service is running. POST to /predict to get risk predictions."}

@app.post("/predict")
def predict_risk(request: PredictionRequest):
    if model is None:
        raise HTTPException(status_code=500, detail="ML Model is not loaded. Please train the model first.")
        
    try:
        # Convert request to DataFrame for the model
        input_data = pd.DataFrame([request.model_dump()])
        
        # XGBoost expects the same column order as training
        expected_cols = ['iyear', 'region', 'country', 'attacktype1', 'targtype1', 'weaptype1']
        input_data = input_data[expected_cols]
        
        # Predict probability of success (class 1)
        prob = model.predict_proba(input_data)[0][1]
        
        # Determine risk level
        if prob >= 0.75:
            risk_level = "High Risk"
        elif prob >= 0.4:
            risk_level = "Medium Risk"
        else:
            risk_level = "Low Risk"
            
        return {
            "status": "success",
            "data": {
                "success_probability": float(prob),
                "risk_level": risk_level
            },
            "message": "Dự báo thành công"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "message": str(e)
        }
