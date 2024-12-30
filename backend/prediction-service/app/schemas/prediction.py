from pydantic import BaseModel
from typing import List, Optional, Any

class PredictionRequest(BaseModel):
    input_data: Any
    model_name: str

class PredictionResponse(BaseModel):
    prediction: Any
    confidence: Optional[float] = None
    model_name: str
    metadata: Optional[dict] = None
