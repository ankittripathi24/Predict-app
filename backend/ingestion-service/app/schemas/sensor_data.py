from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SensorData(BaseModel):
    machine_id: str
    timestamp: datetime
    temperature: float
    vibration: float
    energy_consumption: float
    data_type: str
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True
