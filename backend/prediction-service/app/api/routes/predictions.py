from fastapi import APIRouter, HTTPException
from typing import List
import joblib
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
from schemas.prediction import PredictionResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Load model and scaler
try:
    model = joblib.load("/app/models/trained_model.pkl")
    scaler = joblib.load("/app/models/scaler.pkl")
    logger.info("Successfully loaded model and scaler")
except Exception as e:
    logger.error(f"Error loading model: {str(e)}")
    model = None
    scaler = None

@router.get("/predictions", response_model=List[PredictionResponse])
async def get_predictions():
    if not model or not scaler:
        raise HTTPException(
            status_code=503,
            detail="Model not available"
        )
    
    try:
        current_time = pd.Timestamp.now(tz='UTC')
        predictions = []
        
        # Generate predictions for next hour
        for minute in range(0, 60, 5):
            future_time = current_time + pd.Timedelta(minutes=minute)
            
            # Example features (should be replaced with real data)
            features = np.array([[
                25.0,  # temperature
                0.5,   # vibration
                100,   # energy_consumption
                future_time.hour,
                future_time.weekday(),
                future_time.month
            ]])
            
            features_scaled = scaler.transform(features)
            prediction = model.predict(features_scaled)[0]
            
            predictions.append({
                "timestamp": future_time,
                "prediction": float(prediction),
                "confidence": 0.95  # Example confidence score
            })
        
        return predictions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
