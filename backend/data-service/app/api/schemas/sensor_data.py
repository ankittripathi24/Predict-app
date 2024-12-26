from pydantic import BaseModel
from datetime import datetime

class SensorDataResponse(BaseModel):
    id: int
    timestamp: datetime
    temperature: float
    humidity: float
    pressure: float

    class Config:
        from_attributes = True  # For Pydantic v2