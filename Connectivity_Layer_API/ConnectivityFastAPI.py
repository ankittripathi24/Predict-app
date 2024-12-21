from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import pg8000
import os
import logging
from datetime import datetime, timedelta
from typing import Optional
import traceback
import json
import redis
from functools import lru_cache
import asyncio
import io
import joblib
import numpy as np
from sqlalchemy import create_engine, text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PostgreSQL connection settings
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = "postgres"
DB_PASSWORD = "BVV6Hty6bZ"

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
CACHE_TIMEOUT = 60  # seconds

# Initialize Redis client
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)

logger.debug(f"Database configuration: HOST={DB_HOST}, DB={DB_NAME}, USER={DB_USER}")

async def get_db_connection():
    return pg8000.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        ssl_context=None
    )

def get_cache_key(start_time: Optional[datetime], end_time: Optional[datetime], limit: int, offset: int) -> str:
    """Generate a unique cache key based on query parameters"""
    return f"sensor_data:{start_time.isoformat() if start_time else 'None'}:{end_time.isoformat() if end_time else 'None'}:{limit}:{offset}"

async def get_cached_data(cache_key: str):
    """Get data from Redis cache"""
    try:
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception as e:
        logger.error(f"Redis error: {str(e)}")
    return None

async def set_cached_data(cache_key: str, data: list):
    """Set data in Redis cache"""
    try:
        redis_client.setex(
            cache_key,
            CACHE_TIMEOUT,
            json.dumps(data, default=str)
        )
    except Exception as e:
        logger.error(f"Redis error: {str(e)}")

async def fetch_sensor_data(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 1000,
    offset: int = 0
):
    # Generate cache key
    cache_key = get_cache_key(start_time, end_time, limit, offset)
    logger.info(f"Cache key is: {cache_key}")

    # Try to get data from cache
    cached_data = await get_cached_data(cache_key)
    if cached_data:
        logger.info("Returning data from cache")
        return cached_data
    
    try:
        conn = await get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT machine_id, timestamp, temperature, vibration, energy_consumption,
                   data_type, 
                   metadata_material_type, metadata_pressure_range, metadata_material_thickness,
                   metadata_cutting_speed, metadata_coolant_type,
                   metadata_product_type, metadata_line_speed, metadata_batch_size
            FROM sensor_data
            WHERE ($1::timestamptz IS NULL OR timestamp >= $1)
            AND ($2::timestamptz IS NULL OR timestamp <= $2)
            ORDER BY timestamp DESC
            LIMIT $3 OFFSET $4
        """
        
        cursor.execute(query, (start_time, end_time, limit, offset))
        columns = [
            'machine_id', 'timestamp', 'temperature', 'vibration', 'energy_consumption',
            'data_type',
            'metadata_material_type', 'metadata_pressure_range', 'metadata_material_thickness',
            'metadata_cutting_speed', 'metadata_coolant_type',
            'metadata_product_type', 'metadata_line_speed', 'metadata_batch_size'
        ]
        rows = cursor.fetchall()
        
        data = []
        for row in rows:
            row_dict = {}
            for col, val in zip(columns, row):
                if val is not None:  # Only include non-NULL values
                    row_dict[col] = val
            data.append(row_dict)
        
        # Cache the results
        await set_cached_data(cache_key, data)
        
        return data
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

# Load the trained model and scaler
MODEL_PATH = '/Users/ankittripathi/Documents/Primitive Programmer/Kubernetes/Model_Training/trained_model.pkl'
SCALER_PATH = '/Users/ankittripathi/Documents/Primitive Programmer/Kubernetes/Model_Training/scaler.pkl'

try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    logger.info("Successfully loaded model and scaler")
except Exception as e:
    logger.error(f"Error loading model or scaler: {str(e)}")
    model = None
    scaler = None

def generate_hourly_predictions(latest_data):
    """Generate predictions for the next hour using the trained model."""
    if not model or not scaler:
        raise HTTPException(
            status_code=503,
            detail="Model not available. Please train the model first."
        )

    try:
        # Use UTC for consistency
        current_time = pd.Timestamp.now(tz='UTC')
        predictions = []
        
        # Create feature matrix for next hour predictions
        for minute in range(0, 60, 5):  # Predict every 5 minutes
            future_time = current_time + pd.Timedelta(minutes=minute)
            
            for machine_data in latest_data:
                # Prepare features in the same order as training
                features = np.array([[
                    machine_data['temperature'],
                    machine_data['vibration'],
                    machine_data['energy_consumption'],
                    future_time.hour,
                    future_time.weekday(),
                    future_time.month
                ]])
                
                # Scale features
                features_scaled = scaler.transform(features)
                
                # Make prediction
                prediction = model.predict(features_scaled)[0]
                
                predictions.append({
                    'machine_id': machine_data['machine_id'],
                    'timestamp': future_time.isoformat(),
                    'predicted_values': prediction.tolist()  # Convert numpy array to list
                })
        
        return predictions
    except Exception as e:
        logger.error(f"Error generating predictions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating predictions: {str(e)}"
        )

@app.get("/get-sensor-data")
async def get_sensor_data(
    start_time: Optional[str] = Query(None),
    end_time: Optional[str] = Query(None),
    limit: int = Query(1000, ge=1, le=5000),
    offset: int = Query(0, ge=0)
):
    try:
        # Parse datetime strings if provided
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00')) if start_time else None
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00')) if end_time else None
        
        data = await fetch_sensor_data(start_dt, end_dt, limit, offset)
        return {"message": "Data retrieved successfully", "data": data}
        
    except Exception as e:
        logger.error(f"Error in get_sensor_data: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error fetching sensor data: {str(e)}")

# Maximum file size (1MB = 1_000_000 bytes)
MAX_FILE_SIZE = 1_000_000

class CSVValidationError(Exception):
    pass

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...), data_type: str = Form(...), metadata: str = Form(...)):
    """
    Upload a CSV file with metadata about the manufacturing process
    """
    try:
        logger.info(f"Received file upload: {file.filename}")
        logger.info(f"Data type: {data_type}")
        logger.info(f"Metadata: {metadata}")
        
        # Parse metadata
        metadata_dict = json.loads(metadata)
        
        # Define metadata field types and their conversion functions
        valid_metadata_fields = {
            'material_type': (str, lambda x: str(x)),
            'pressure_range': (str, lambda x: str(x)),
            'material_thickness': (float, lambda x: float(x) if isinstance(x, (int, float, str)) and str(x).replace('.', '').isdigit() else None),
            'cutting_speed': (float, lambda x: float(x) if isinstance(x, (int, float, str)) and str(x).replace('.', '').isdigit() else None),
            'coolant_type': (str, lambda x: str(x)),
            'product_type': (str, lambda x: str(x)),
            'line_speed': (float, lambda x: float(x) if isinstance(x, (int, float, str)) and str(x).replace('.', '').isdigit() else None),
            'batch_size': (int, lambda x: int(float(x)) if isinstance(x, (int, float, str)) and str(x).replace('.', '').isdigit() else None)
        }
        
        # Create a new metadata dictionary with validated fields
        validated_metadata = {}
        for field, (expected_type, converter) in valid_metadata_fields.items():
            if field in metadata_dict:
                try:
                    value = metadata_dict[field]
                    converted_value = converter(value)
                    if converted_value is not None:
                        validated_metadata[f'metadata_{field}'] = converted_value
                    else:
                        logger.warning(f"Skipping invalid value for {field}: {value}")
                except (ValueError, TypeError) as e:
                    logger.warning(f"Could not convert {field} value: {value}. Error: {str(e)}")
                    # Skip invalid values instead of raising an error
                    continue
        
        # Read CSV content
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")
            
        df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        
        # Validate required columns
        required_columns = {'temperature', 'vibration', 'energy_consumption', 'machine_id'}
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        # Add metadata columns to the dataframe
        for column, value in validated_metadata.items():
            df[column] = value
        
        # Add data type
        df['data_type'] = data_type
        
        # Add timestamp if not present
        if 'timestamp' not in df.columns:
            df['timestamp'] = pd.Timestamp.now(tz='Asia/Kolkata')
        else:
            # Convert timestamp to datetime if it exists
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Store in database
        DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"
        engine = create_engine(DATABASE_URL)
        
        # Ensure all column names match the database schema
        df.columns = [col.lower() for col in df.columns]
        
        try:
            df.to_sql('sensor_data', engine, if_exists='append', index=False)
            logger.info(f"Successfully uploaded {len(df)} rows with metadata")
            return {
                "message": "File uploaded successfully", 
                "rows_processed": len(df),
                "metadata_processed": validated_metadata
            }
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
            
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid metadata JSON format")
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="Empty CSV file")
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# Create SQLAlchemy engine
engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')

# Add metadata columns to the table
def setup_database():
    try:
        with engine.connect() as connection:
            # Create a text object from the SQL statement
            sql = text("""
                ALTER TABLE sensor_data 
                ADD COLUMN IF NOT EXISTS data_type VARCHAR(50),
                ADD COLUMN IF NOT EXISTS metadata_material_type VARCHAR(50),
                ADD COLUMN IF NOT EXISTS metadata_pressure_range VARCHAR(50),
                ADD COLUMN IF NOT EXISTS metadata_material_thickness FLOAT,
                ADD COLUMN IF NOT EXISTS metadata_cutting_speed FLOAT,
                ADD COLUMN IF NOT EXISTS metadata_coolant_type VARCHAR(50),
                ADD COLUMN IF NOT EXISTS metadata_product_type VARCHAR(50),
                ADD COLUMN IF NOT EXISTS metadata_line_speed FLOAT,
                ADD COLUMN IF NOT EXISTS metadata_batch_size INTEGER;
            """)
            # Execute the SQL statement
            connection.execute(sql)
            connection.commit()
            logger.info("Database schema updated successfully")
    except Exception as e:
        logger.error(f"Error updating database schema: {str(e)}")
        raise

# Call setup_database when the app starts
@app.on_event("startup")
async def startup_event():
    setup_database()

async def get_or_generate_predictions():
    """Get cached predictions or generate new ones if needed."""
    try:
        # Use IST date for cache key
        today = pd.Timestamp.now(tz='Asia/Kolkata').strftime('%Y-%m-%d')
        cache_key = f"predictions:{today}"
        
        # Try to get cached predictions
        cached_data = redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        
        # If no cached data, generate new predictions
        query = """
            SELECT machine_id, temperature, vibration, energy_consumption, timestamp
            FROM sensor_data
            WHERE timestamp >= NOW() - INTERVAL '1 hour'
            ORDER BY timestamp DESC
            LIMIT 1
        """
        conn = await get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        latest_data = cursor.fetchall()
        conn.close()
        
        if not latest_data:
            return {
                "lastUpdated": pd.Timestamp.now(tz='Asia/Kolkata').isoformat(),
                "devices": [],
                "message": "No sensor data available for predictions"
            }
            
        # Generate new predictions
        predictions = generate_hourly_predictions(latest_data)
        
        # Format response
        response = {
            "lastUpdated": pd.Timestamp.now(tz='Asia/Kolkata').isoformat(),
            "devices": []
        }
        
        for machine_pred in predictions:
            # Calculate maintenance probability based on predicted values
            pred_values = machine_pred['predicted_values']
            threshold = 0.7
            
            maintenance_needed = any(val > threshold for val in pred_values)
            probability = max(pred_values) if pred_values else 0.5
            
            issues = []
            if pred_values[0] > threshold:
                issues.append("High temperature predicted")
            if pred_values[1] > threshold:
                issues.append("High vibration levels predicted")
            if pred_values[2] > threshold:
                issues.append("High energy consumption predicted")
                
            device_pred = {
                "id": f"sensor-{machine_pred['machine_id']}",
                "name": f"Machine {machine_pred['machine_id']}",
                "prediction": {
                    "maintenanceNeeded": maintenance_needed,
                    "probability": min(probability, 0.95),
                    "estimatedTimeToFailure": "1 hour" if maintenance_needed else "24 hours",
                    "issues": issues,
                    "predicted_timeline": [
                        {
                            "timestamp": pred['timestamp'],
                            "values": pred['predicted_values']
                        } for pred in predictions 
                        if pred['machine_id'] == machine_pred['machine_id']
                    ]
                }
            }
            response["devices"].append(device_pred)
            
        # Cache predictions for 24 hours
        redis_client.setex(
            cache_key,
            24 * 60 * 60,  # 24 hours
            json.dumps(response)
        )
        
        return response
    except redis.ConnectionError as e:
        logger.error(f"Redis connection error: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Cache service unavailable. Please try again later."
        )
    except Exception as e:
        logger.error(f"Error generating predictions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating predictions: {str(e)}"
        )

@app.get("/get-predictions")
async def get_predictions():
    """Get factory-wide maintenance predictions from Redis cache."""
    try:
        # Get predictions from cache or generate new ones
        predictions_data = await get_or_generate_predictions()
        logger.info(f"Prediction data: {json.dumps(predictions_data)}")

        # Group predictions by data type and metadata
        grouped_predictions = {}
        for device in predictions_data.get('devices', []):
            prediction = device['prediction']
            
            # Create a unique key for each data type and metadata combination
            key = f"{device.get('data_type', 'default')}"
            
            if key not in grouped_predictions:
                grouped_predictions[key] = {
                    'dataType': device.get('data_type', 'default'),
                    'metadata': device.get('metadata', {}),
                    'prediction': {
                        'maintenanceNeeded': prediction['maintenanceNeeded'],
                        'probability': prediction['probability'],
                        'estimatedTimeToMaintenance': prediction.get('estimatedTimeToFailure', '24 hours'),
                        'issues': prediction['issues'],
                        'predictions': []
                    }
                }
            
            # Add prediction timeline data
            if 'predicted_timeline' in prediction:
                for point in prediction['predicted_timeline']:
                    grouped_predictions[key]['prediction']['predictions'].append({
                        'timestamp': point['timestamp'],
                        'temperature': point['values'][0],
                        'vibration': point['values'][1],
                        'energy': point['values'][2]
                    })

        # Format the response as expected by the frontend
        response = {
            'lastUpdated': predictions_data.get('lastUpdated', pd.Timestamp.now(tz='Asia/Kolkata').isoformat()),
            'groups': list(grouped_predictions.values())
        }

        if not response['groups']:
            response['message'] = "No predictions available"

        return response

    except Exception as e:
        logger.error(f"Error getting predictions: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
