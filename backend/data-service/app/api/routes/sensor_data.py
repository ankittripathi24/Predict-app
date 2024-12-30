from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from ...database import get_db
from ..models.sensor_data import SensorData
from ..schemas.sensor_data import SensorDataResponse

router = APIRouter()

@router.get("/get-sensor-data", response_model=List[SensorDataResponse])
async def get_sensor_data(
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    limit: int = Query(1000, ge=1, le=5000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    try:
        query = db.query(SensorData)
        
        if start_time:
            query = query.filter(SensorData.timestamp >= start_time)
        if end_time:
            query = query.filter(SensorData.timestamp <= end_time)
            
        total = query.count()
        data = query.order_by(SensorData.timestamp.desc()).offset(offset).limit(limit).all()
        
        return {
            "data": data,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
