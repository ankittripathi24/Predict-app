from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import pandas as pd
from datetime import datetime
import logging

from app.database import get_db
from app.schemas.sensor_data import SensorData

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/upload")
async def upload_data(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    try:
        # Read the CSV file
        contents = await file.read()
        df = pd.read_csv(pd.io.common.BytesIO(contents))
        
        # Validate required columns
        required_columns = ['machine_id', 'timestamp', 'temperature', 'vibration', 'energy_consumption']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        # Convert timestamp strings to datetime objects
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Create SensorData objects
        sensor_data_objects = []
        for _, row in df.iterrows():
            try:
                sensor_data = SensorData(
                    machine_id=str(row['machine_id']),
                    timestamp=row['timestamp'],
                    temperature=float(row['temperature']),
                    vibration=float(row['vibration']),
                    energy_consumption=float(row['energy_consumption']),
                    data_type='sensor_reading'
                )
                sensor_data_objects.append(sensor_data)
            except Exception as e:
                logger.error(f"Error processing row: {row}, Error: {str(e)}")
                continue
        
        # Add to database
        for sensor_data in sensor_data_objects:
            db.add(sensor_data)
        db.commit()
        
        return {
            "message": "Upload successful",
            "rows_processed": len(sensor_data_objects),
            "total_rows": len(df)
        }
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
