from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from sqlalchemy.orm import Session
import pandas as pd
import json
from app.database import get_db
from models.sensor_data import SensorData
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 1_000_000  # 1MB

@router.post("/upload")
async def upload_csv(
    file: UploadFile = File(...),
    data_type: str = Form(...),
    metadata: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # Validate file size
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large")
            
        # Parse CSV
        df = pd.read_csv(pd.io.common.BytesIO(content))
        
        # Parse metadata
        metadata_dict = json.loads(metadata)
        
        # Validate required columns
        required_columns = ['machine_id', 'timestamp', 'temperature', 'vibration', 'energy_consumption']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(status_code=400, detail="Missing required columns")
            
        # Process and save data
        records = []
        for _, row in df.iterrows():
            record = SensorData(
                machine_id=row['machine_id'],
                timestamp=pd.to_datetime(row['timestamp']),
                temperature=row['temperature'],
                vibration=row['vibration'],
                energy_consumption=row['energy_consumption'],
                data_type=data_type,
                **metadata_dict
            )
            records.append(record)
            
        db.bulk_save_objects(records)
        db.commit()
        
        return {"message": f"Successfully processed {len(records)} records"}
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
