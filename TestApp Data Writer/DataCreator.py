import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_sensor_data(num_machines=10, days=365):
    data = []
    for machine_id in range(num_machines):
        for day in range(days):
            temperature = np.random.normal(50, 10)
            vibration = np.random.normal(0.5, 0.1)
            energy_consumption = np.random.normal(100, 20)
            
            # Simulate degradation
            if day > 300:
                temperature += np.random.normal(5, 2)
                vibration += np.random.normal(0.2, 0.05)
            
            data.append({
                'machine_id': machine_id,
                'timestamp': datetime.now() - timedelta(days=day),
                'temperature': temperature,
                'vibration': vibration,
                'energy_consumption': energy_consumption
            })
    
    return pd.DataFrame(data)

if __name__ == '__main__':
    data = generate_sensor_data(num_machines=2, days=2)
    print(data)