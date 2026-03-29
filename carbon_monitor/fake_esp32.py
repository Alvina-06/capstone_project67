# fake_esp32.py

import requests
import random
import time
from datetime import datetime

# Your Flask server URL
URL = "http://127.0.0.1:5000/api/sensor/data"

print("Fake ESP32 started...")
print(f"Sending data to: {URL}")
print("Press CTRL+C to stop\n")

while True:
    try:
        hour = datetime.now().hour

        # Simulate higher usage in evening
        if 18 <= hour <= 22:
            power  = random.uniform(2.5, 4.0)
            co2    = random.uniform(900, 1400)
        else:
            power  = random.uniform(0.5, 2.0)
            co2    = random.uniform(400, 800)

        data = {
            "device_id":   "ESP32_001",
            "power_kw":    round(power, 2),
            "time_seconds": 5,
            "co2_ppm":     round(co2, 1),
            "temperature": round(random.uniform(24, 32), 1),
            "voltage":     round(random.uniform(218, 222), 1),
            "timestamp":   datetime.now().isoformat()
        }

        response = requests.post(URL, json=data)
        result   = response.json()

        print(f"[{datetime.now().strftime('%H:%M:%S')}] "
              f"power={data['power_kw']}kW | "
              f"co2={data['co2_ppm']}ppm | "
              f"carbon={result.get('carbon_kg')}kg | "
              f"anomaly={result.get('anomaly')} | "
              f"status={response.status_code}")

    except Exception as e:
        print(f"Error: {e}")

    time.sleep(5)