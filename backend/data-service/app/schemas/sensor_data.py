from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class SensorData(BaseModel):
    sensor_id: str
    timestamp: datetime
    value: float
    type: str
    metadata: Optional[dict] = None

class SensorDataResponse(BaseModel):
    data: List[SensorData]
    count: int
    metadata: Optional[dict] = None

class SensorDataStats(BaseModel):
    sensor_id: str
    min_value: float
    max_value: float
    avg_value: float
    count: int
    start_time: datetime
    end_time: datetime
