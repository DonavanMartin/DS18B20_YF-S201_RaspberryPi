# -*- coding: utf-8 -*-
"""
Connection and write to InfluxDB 1.8 (compatible with Raspberry Pi Zero 32-bit)
Uses influxdb-python library (pip install influxdb)
"""

from influxdb import InfluxDBClient
import datetime
from datetime import timezone

# ────────────────────────────────────────────────
# CONFIGURATION – CUSTOMIZE AS NEEDED
# ────────────────────────────────────────────────
INFLUX_HOST = "localhost"          # or Pi's IP if remote
INFLUX_PORT = 8086
INFLUX_USER = "admin"              # user created in InfluxDB 1.8
INFLUX_PASS = "misericorde"        # password (change it!)
INFLUX_DB   = "mesures"            # database name

# ────────────────────────────────────────────────
# Create client
# ────────────────────────────────────────────────
client = InfluxDBClient(
    host=INFLUX_HOST,
    port=INFLUX_PORT,
    username=INFLUX_USER,
    password=INFLUX_PASS,
    database=INFLUX_DB,
    timeout=10000  # 10 seconds
)

print("[DB] InfluxDB 1.8 Connection: OK → database '{INFLUX_DB}'")

def sendJSON(json_data, sensor_type="UNKNOWN", debug=False):
    """
    Sends data points to InfluxDB 1.8.
    
    Args:
        json_data: Data formatted as list of dicts or single dict
        sensor_type: Identifier for log messages (e.g., "TEMP", "FLOW")
        debug: If True, print success messages; errors always printed
    
    Accepts the same format as your previous code:
    - A list of dictionaries
    - A single dictionary

    Expected format:
    [
        {
            "measurement": "temperature",
            "tags": {"room": "salon", "sensor": "temp01"},
            "fields": {"value": 22.5, "humidity": 48.3},
            "time": datetime.datetime.now(datetime.timezone.utc)  # optional (default is now())
        },
        ...
    ]
    """
    try:
        # If it's a single dict → put it in a list
        if isinstance(json_data, dict):
            json_data = [json_data]

        if not isinstance(json_data, list):
            raise ValueError("Expected format: dict or list[dict]")

        # Format compatible with write_points (InfluxDB 1.x)
        points = []
        for item in json_data:
            point = {
                "measurement": item["measurement"],
                "tags": item.get("tags", {}),
                "fields": item.get("fields", {}),
            }
            # Optional timestamp
            if "time" in item:
                point["time"] = item["time"]
            points.append(point)

        # Write to database
        client.write_points(points)
        if debug:
            print(f"[{sensor_type}] [DB] Write successful: {len(points)} point(s) sent to '{INFLUX_DB}'")

    except Exception as e:
        print(f"[{sensor_type}] [DB] [ERROR] Send failed: {e}")
        # You can add retry logic, logging, etc. here


# ────────────────────────────────────────────────
# Usage example (same format as your previous code)
# ────────────────────────────────────────────────
if __name__ == "__main__":
    # Example with multiple measurements
    data = [
        {
            "measurement": "temperature",
            "tags": {"room": "salon", "sensor": "temp01"},
            "fields": {"value": 22.5, "humidity": 48.3},
            "time": datetime.datetime.utcnow()
        },
        {
            "measurement": "flow",
            "tags": {"sensor": "YF-S201", "location": "eau froide"},
            "fields": {"debit_l_min": 3.8, "total_l": 1452.7}
        },
        {
            "measurement": "onewire",
            "tags": {"device": "DS18B20", "id": "28-01123456789a"},
            "fields": {"temperature": 19.4}
        }
    ]

    sendJSON(data)

    # Example with a single point
    single = {
        "measurement": "cpu",
        "tags": {"host": "raspberrypi-zero"},
        "fields": {"usage": 12.3}
    }
    sendJSON(single)

    # Best practice: close the connection at the end of the program
    # client.close()  # uncomment if you have multiple sessions