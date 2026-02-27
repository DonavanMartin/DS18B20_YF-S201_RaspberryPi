#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulation of 8 DS18B20 sensors to test sending data to InfluxDB 1.8
Generates realistic temperatures (between 18 and 28 °C) with slight variation
"""

import time
import random
from datetime import datetime
import sys
import os

# Path to your DBconnection module
scriptPath = os.path.realpath(os.path.dirname(sys.argv[0]))
os.chdir(scriptPath)
sys.path.append("../InfluxDB")
import DBconnection

INFLUX_ENABLE = 'yes'

# ────────────────────────────────────────────────
# Simulation configuration
# ────────────────────────────────────────────────
NB_DEVICES = 8
BASE_SERIAL = "28-02123456"  # Common prefix for simulated serials

# Realistic temperature range for a room (in °C)
TEMP_MIN = 18.0
TEMP_MAX = 28.0

# Max variation per tick (to simulate natural evolution)
VARIATION_MAX = 0.4

# Storage of current temperatures (for progressive evolution)
current_temps = [random.uniform(TEMP_MIN + 2, TEMP_MAX - 2) for _ in range(NB_DEVICES)]

# ────────────────────────────────────────────────
# Generation of simulated devices
# ────────────────────────────────────────────────
def getDevices():
    devices = []
    for i in range(NB_DEVICES):
        serial = f"{BASE_SERIAL}{i:02d}"  # ex: 28-0212345600, 28-0212345601, ...
        devices.append({
            "path": f"/sys/bus/w1/devices/{serial}/w1_slave",  # fictional
            "type": "Temperature",
            "serial": serial
        })
    print(f"Simulating {len(devices)} DS18B20 sensors")
    return devices, len(devices)


# ────────────────────────────────────────────────
# Simulated reading
# ────────────────────────────────────────────────
def read_ext_temp(device_index):
    # Progressive evolution + small random noise
    current = current_temps[device_index]
    delta = random.uniform(-VARIATION_MAX, VARIATION_MAX)
    new_temp = current + delta
    
    # Constrain to realistic range
    new_temp = max(TEMP_MIN, min(TEMP_MAX, new_temp))
    
    current_temps[device_index] = new_temp
    return round(new_temp, 3)


# ────────────────────────────────────────────────
# Main loop
# ────────────────────────────────────────────────
try:
    while True:
        time.sleep(1)  # 1 second interval (adjust as needed)

        devices, nb_device = getDevices()

        current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        for i in range(nb_device):
            dev = devices[i]
            ext_temp = read_ext_temp(i)

            print(f"Serial: {dev['serial']}  -- Type: {dev['type']}  -- Temp C: {ext_temp:.3f}  -- Temp F: {(ext_temp * 9/5 + 32):.2f}")

            if INFLUX_ENABLE.lower() == 'yes':
                json_body = [{
                    "measurement": "temperature",
                    "tags": {
                        "serial": dev['serial'],
                        "type": dev['type']
                    },
                    "time": current_time,
                    "fields": {
                        "value": ext_temp
                    }
                }]

                try:
                    DBconnection.sendJSON(json_body)
                    print(f"  → Sent to InfluxDB for {dev['serial']}")
                except Exception as e:
                    print(f"  → InfluxDB send error: {e}")

except KeyboardInterrupt:
    print("\nProgram stopped by Ctrl+C")
    sys.exit(0)
except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)