import os
import pg8000
import paho.mqtt.client as mqtt
from datetime import datetime

# Database connection settings from environment variables
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_NAME = os.getenv("DB_NAME", "postgres")

DB_USER = os.gos.getenv("DB_PASSWORD", 'postgres')
DB_PASSWORD = os.getenv("DB_PASSWORD", 'BVV6Hty6bZZ')

# Define a function to check if the user exists in PostgreSQL
def check_user_exists(cursor):
    cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s;", (DB_USER,))
    return cursor.fetchone() is not None

# Define a function to check if the table exists in PostgreSQL
def check_table_exists(cursor):
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 
            FROM information_schema.tables 
            WHERE table_name = 'sensor_data'
        );
    """)
    return cursor.fetchone()[0]

# Define a function to insert data into PostgreSQL
def insert_data(machine_id, timestamp, temperature, vibration, energy_consumption):
    try:
        conn = pg8000.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
        cursor = conn.cursor()

        # Check if user exists
        if not check_user_exists(cursor):
            print("Database user does not exist.")
            return

        # Check if table exists
        if not check_table_exists(cursor):
            print("Table 'sensor_data' does not exist.")
            return

        # Insert data into the database
        cursor.execute(
            "INSERT INTO sensor_data (machine_id, timestamp, temperature, vibration, energy_consumption) VALUES (%s, %s, %s, %s, %s)",
            (machine_id, timestamp, temperature, vibration, energy_consumption)
        )
        conn.commit()
        print(f"Inserted data: Machine ID={machine_id}, Timestamp={timestamp}, Temperature={temperature}, Vibration={vibration}, Energy Consumption={energy_consumption}")

    except Exception as e:
        print(f"An error occurred while inserting data: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# MQTT callback for when a message is received
def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    print(f"Received message: {msg.topic} {msg.payload.decode()}")

    # Parse the received message (assuming it's in CSV format)
    machine_id, timestamp_str, temperature, vibration, energy_consumption = msg.payload.decode().split(',')
    
    # Convert timestamp to datetime object if needed (optional)
    timestamp = datetime.fromisoformat(timestamp_str)

    # Insert received data into PostgreSQL
    insert_data(machine_id, timestamp, float(temperature), float(vibration), float(energy_consumption))

def publish_sensor_data(broker_url, machine_id, timestamp_str, temperature, vibration, energy_consumption):
    """Publish sensor data to MQTT broker."""
    
    # Set up MQTT client and callbacks
    mqtt_client = mqtt.Client()
    mqtt_client.on_message = on_message

    # Connect to the MQTT broker and subscribe to the topic
    mqtt_client.connect(broker_url)
    
    # Prepare message payload
    payload = f"{machine_id},{timestamp_str},{temperature},{vibration},{energy_consumption}"
    
    # Publish the sensor data to MQTT broker
    mqtt_client.publish("sensor/data", payload)
    
    print(f"Published new sensor data: {payload}")

    # Start the MQTT loop in a separate thread to handle incoming messages
    mqtt_client.loop_start()

    try:
        print(f"Connected to MQTT broker at {broker_url}. Waiting for messages...")
        
        while True:
            time.sleep(1)  # Keep running

    except KeyboardInterrupt:
        print("Exiting...")

    finally:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()

def main():
    # Ask user for MQTT broker URL or use default
    broker_url = input("Enter MQTT Broker URL (or press Enter for default 'mqtt.eclipseprojects.io'): ") or "mqtt.eclipseprojects.io"
    
    # Collect sensor data from user input
    machine_id = input("Enter Machine ID: ")
    
    timestamp_str = input("Enter Timestamp (ISO format) or press Enter for current time: ")
    if not timestamp_str:
        timestamp_str = datetime.now().isoformat()  # Use current time if none provided
    
    temperature = float(input("Enter Temperature: "))
    vibration = float(input("Enter Vibration: "))
    energy_consumption = float(input("Enter Energy Consumption: "))

    # Publish sensor data using provided inputs
    publish_sensor_data(broker_url, machine_id, timestamp_str, temperature, vibration, energy_consumption)

if __name__ == "__main__":
    main()
