# data_creator.py
import time
import random
import paho.mqtt.client as mqtt

# MQTT settings
MQTT_BROKER = "localhost"
MQTT_TOPIC = "iot/sensor_data"

# Connect to MQTT broker
client = mqtt.Client()
client.connect(MQTT_BROKER)

def generate_data():
    # Simulate sensor data
    temperature = random.uniform(20.0, 30.0)  # Random temperature between 20-30°C
    vibration = random.uniform(0.0, 5.0)      # Random vibration level
    return {"temperature": temperature, "vibration": vibration}

while True:
    data = generate_data()
    client.publish(MQTT_TOPIC, str(data))  # Publish data to MQTT topic
    print(f"Published: {data}")
    time.sleep(60)  # Wait for 1 minute before generating new data
