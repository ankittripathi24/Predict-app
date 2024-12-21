import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import mlflow
import mlflow.sklearn
import logging
import redis
import json
from datetime import datetime, timedelta
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis configuration
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

# Initialize Redis client
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)

def load_data_from_csv(csv_file_path):
    """Load data from CSV file."""
    try:
        df = pd.read_csv(csv_file_path)
        logger.info(f"Successfully loaded data from {csv_file_path}")
        return df
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        raise

def preprocess_data(df):
    """Preprocess the data for training."""
    try:
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Extract time-based features
        df['hour'] = df['timestamp'].dt.hour
        df['day'] = df['timestamp'].dt.dayofweek
        df['month'] = df['timestamp'].dt.month
        
        # Select features for prediction
        features = ['temperature', 'vibration', 'energy_consumption', 'hour', 'day', 'month']
        X = df[features]
        
        # Create target variables (next hour's values)
        y = df[['temperature', 'vibration', 'energy_consumption']].shift(-12)  # Assuming 5-minute intervals
        
        # Remove rows with NaN values (last 12 rows)
        X = X[:-12]
        y = y[:-12]
        
        # Scale the features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Save the scaler for later use
        joblib.dump(scaler, 'scaler.pkl')
        
        logger.info("Successfully preprocessed data")
        return X_scaled, y, scaler
    except Exception as e:
        logger.error(f"Error preprocessing data: {str(e)}")
        raise

def train_model(X, y):
    """Train a Random Forest model."""
    try:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Initialize and train the model
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        
        # Make predictions on test set
        predictions = model.predict(X_test)
        
        # Calculate metrics
        mse = mean_squared_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        
        logger.info(f"Model Training Metrics:")
        logger.info(f"Mean Squared Error: {mse}")
        logger.info(f"R² Score: {r2}")

        # Log model and metrics to MLflow
        with mlflow.start_run():
            mlflow.sklearn.log_model(model, "model")
            mlflow.log_params({
                "n_estimators": 100,
                "max_depth": 10
            })
            mlflow.log_metrics({
                "mse": mse,
                "r2": r2
            })

        return model
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        raise

def generate_daily_predictions(model, scaler, latest_data):
    """Generate factory-wide maintenance predictions and store in Redis."""
    try:
        logger.info("Starting to generate daily predictions")
        current_time = pd.Timestamp.now(tz='Asia/Kolkata')
        logger.info(f"Current time in IST: {current_time}")
        
        # Group data by data type and metadata
        data_groups = []
        for data_type in latest_data['data_type'].unique():
            type_data = latest_data[latest_data['data_type'] == data_type]
            
            # Get metadata columns for this data type
            metadata_cols = [col for col in type_data.columns if col.startswith('metadata_')]
            
            # Group by metadata values
            metadata_groups = type_data.groupby(metadata_cols)
            
            for metadata_values, group_data in metadata_groups:
                metadata_dict = dict(zip([col.replace('metadata_', '') for col in metadata_cols], metadata_values))
                
                # Calculate average sensor values for this group
                avg_temperature = group_data['temperature'].mean()
                avg_vibration = group_data['vibration'].mean()
                avg_energy = group_data['energy_consumption'].mean()
                
                # Generate predictions for this group
                predictions = []
                for hour in range(24):
                    prediction_time = current_time.normalize() + pd.Timedelta(hours=hour)
                    features = np.array([[
                        avg_temperature,
                        avg_vibration,
                        avg_energy,
                        prediction_time.hour,
                        prediction_time.dayofweek,
                        prediction_time.month
                    ]])
                    
                    features_scaled = scaler.transform(features)
                    prediction = model.predict(features_scaled)[0]
                    
                    predictions.append({
                        'timestamp': prediction_time.isoformat(),
                        'temperature': float(prediction[0]),
                        'vibration': float(prediction[1]),
                        'energy': float(prediction[2])
                    })
                
                # Analyze predictions for maintenance needs based on data type
                if data_type == 'pressing':
                    # Adjust thresholds based on material type
                    material_type = metadata_dict.get('material_type', 'Unknown')
                    if material_type == 'Metal':
                        threshold_temp = 100  # Higher temperature threshold for metals
                        threshold_vibration = 80  # Higher vibration threshold
                        threshold_energy = 95  # Higher energy threshold
                    elif material_type == 'Plastic':
                        threshold_temp = 60  # Lower temperature threshold for plastics
                        threshold_vibration = 50  # Lower vibration threshold
                        threshold_energy = 70  # Lower energy threshold
                    else:
                        threshold_temp = 80  # Default thresholds
                        threshold_vibration = 70
                        threshold_energy = 90
                        
                elif data_type == 'machining':
                    # Adjust thresholds based on material and cutting speed
                    material_type = metadata_dict.get('material_type', 'Unknown')
                    cutting_speed = metadata_dict.get('cutting_speed', 'Medium')
                    
                    if material_type == 'Titanium':
                        threshold_temp = 120  # Higher temperature threshold for titanium
                        threshold_vibration = 90
                        threshold_energy = 95
                    elif cutting_speed == 'High (15000+)':
                        threshold_temp = 100
                        threshold_vibration = 85
                        threshold_energy = 90
                    else:
                        threshold_temp = 80
                        threshold_vibration = 70
                        threshold_energy = 85
                        
                else:  # Default thresholds for other types
                    threshold_temp = 80
                    threshold_vibration = 70
                    threshold_energy = 90
                
                # Check if any predictions exceed thresholds
                high_temp_hours = [p for p in predictions if p['temperature'] > threshold_temp]
                high_vibration_hours = [p for p in predictions if p['vibration'] > threshold_vibration]
                high_energy_hours = [p for p in predictions if p['energy'] > threshold_energy]
                
                # Calculate maintenance probability
                total_violations = len(high_temp_hours) + len(high_vibration_hours) + len(high_energy_hours)
                max_possible_violations = len(predictions) * 3
                maintenance_probability = min(0.95, total_violations / max_possible_violations)
                
                # Create context-aware issues list
                issues = []
                if high_temp_hours:
                    if data_type == 'pressing':
                        issues.append(f"High temperature detected for {metadata_dict.get('material_type', 'material')} pressing in {len(high_temp_hours)} hours")
                    elif data_type == 'machining':
                        issues.append(f"High temperature detected while machining {metadata_dict.get('material_type', 'material')} at {metadata_dict.get('cutting_speed', 'normal')} speed in {len(high_temp_hours)} hours")
                    else:
                        issues.append(f"High temperature predicted in {len(high_temp_hours)} hours")
                        
                if high_vibration_hours:
                    if data_type == 'pressing':
                        issues.append(f"High vibration levels for {metadata_dict.get('pressure_range', 'normal pressure')} pressing in {len(high_vibration_hours)} hours")
                    elif data_type == 'machining':
                        issues.append(f"High vibration levels with {metadata_dict.get('coolant_type', 'coolant')} in {len(high_vibration_hours)} hours")
                    else:
                        issues.append(f"High vibration levels predicted in {len(high_vibration_hours)} hours")
                        
                if high_energy_hours:
                    issues.append(f"High energy consumption predicted in {len(high_energy_hours)} hours")
                
                # Add group prediction to results
                data_groups.append({
                    "dataType": data_type,
                    "metadata": metadata_dict,
                    "prediction": {
                        "maintenanceNeeded": maintenance_probability > 0.5,
                        "probability": float(maintenance_probability),
                        "estimatedTimeToMaintenance": "1 hour" if maintenance_probability > 0.8 else "24 hours",
                        "issues": issues,
                        "averageReadings": {
                            "temperature": float(avg_temperature),
                            "vibration": float(avg_vibration),
                            "energy": float(avg_energy)
                        },
                        "predictions": predictions[:6]  # First 6 hours of predictions
                    }
                })
        
        # Format final response
        response = {
            "lastUpdated": current_time.isoformat(),
            "groups": data_groups
        }
        
        # Store in Redis
        cache_key = f"predictions:{current_time.strftime('%Y-%m-%d')}"
        logger.info(f"Using cache key: {cache_key}")
        
        try:
            redis_client.ping()
            logger.info("Redis connection successful")
            redis_result = redis_client.setex(
                cache_key,
                24 * 60 * 60,  # 24 hours expiry
                json.dumps(response)
            )
            logger.info(f"Redis storage result: {redis_result}")
            logger.info(f"Stored predictions in Redis with key: {cache_key}")
            
            stored_data = redis_client.get(cache_key)
            if stored_data:
                logger.info("Successfully verified data storage in Redis")
            else:
                logger.error("Data was not stored in Redis properly")
            
        except redis.ConnectionError as e:
            logger.error(f"Redis connection error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error storing predictions in Redis: {str(e)}")
            raise
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating predictions: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

def save_model(model):
    """Save the trained model to disk."""
    try:
        joblib.dump(model, 'trained_model.pkl')
        logger.info("Model saved successfully as 'trained_model.pkl'")
    except Exception as e:
        logger.error(f"Error saving model: {str(e)}")
        raise

def main():
    try:
        # Path to your exported CSV file
        csv_file_path = '../Data_Export/sensor_data_export.csv'
        
        # Load and preprocess data
        data = load_data_from_csv(csv_file_path)
        
        if data.empty:
            logger.warning("No data found for training")
            return
        
        # Preprocess data
        X, y, scaler = preprocess_data(data)
        
        # Train the model
        model = train_model(X, y)
        
        # Save the model
        save_model(model)
        
        # Generate and store predictions for today
        predictions = generate_daily_predictions(model, scaler, data)
        logger.info("Daily predictions generated and stored in Redis")
        
        logger.info("Model training and prediction generation completed successfully")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()
