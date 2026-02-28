#!/usr/bin/env python
# ════════════════════════════════════════════════════════════════════════════════
# DS18B20 Temperature Sensor - Production/Debug Mode Configuration
# ════════════════════════════════════════════════════════════════════════════════
# --debug → Print all measurements and debug info to console
# (no --debug) → Silent operation, only print on startup and errors

import os
import glob
import time
import sys
import argparse
import threading
from queue import Queue
from datetime import datetime
from datetime import timezone

# Enable line buffering for immediate console output
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1)

# Command-line argument parsing
parser = argparse.ArgumentParser(description='DS18B20 temperature sensor application for Raspberry Pi')
parser.add_argument('--debug', action='store_true', default=False, help='Enable debug mode with verbose logging')
args = parser.parse_args()
DEBUG = args.debug

# Database Connection
scriptPath = os.path.realpath(os.path.dirname(sys.argv[0]))
os.chdir(scriptPath)
sys.path.append("../InfluxDB")
import DBconnection
INFLUX_ENABLE = 'yes'

print("[START] DS18B20 Temperature Sensor starting")
if DEBUG:
    print("[MODE] Debug mode - Verbose logging enabled")
else:
    print("[MODE] Production mode - Silent operation (errors only)")

# Each DS18B20 sensor has a hashed directory
def getDevices():
  base_dir = '/sys/bus/w1/devices/'
  device_folder = glob.glob(base_dir + '28*')
  nb_device = len(device_folder)
  if DEBUG:
      print(f"[TEMP] [INFO] Found {nb_device} DS18B20 device(s)")

  # Create a list containing device info: ['Directory folder', "type", "serial"]
  device = [[0 for x in range(3)] for y in range(nb_device)]
  for x in range(0,nb_device):
    device[x][0] = device_folder[x] + '/w1_slave'
    device[x][1] = "Temperature"
    device[x][2] = device_folder[x].replace(base_dir, '')
    if DEBUG:
        print(f"[TEMP]   [DEVICE {x}] {device[x][2]}")  
  return device, nb_device
 
def convert_from_raw(raw):
  '''
  Convert raw millidegrees to standard decimal format
  '''
  _raw = float(raw) / 1000.0
  return _raw

def convert_to_f(temp_c):
  '''
  Convert Celsius to Fahrenheit
  '''
  return temp_c * 9.0 / 5.0 + 32.0

def read_ext_temp(sensor_file):
  '''
  Read temperature from DS18B20 thermometer (optimized version)
  Reads only until finding the temperature line, using efficient parsing.
  '''
  try:
    with open(sensor_file, 'r') as f:
      for line in f:
        # Temperature is at the end of the last line, format: "...t=20500"
        if 't=' in line:
          # Extract value after "t=" without string splitting
          temp_raw = line.split('t=')[-1].strip()
          return convert_from_raw(float(temp_raw))
  except Exception as e:
    print(f"[TEMP] [ERROR] Failed to read {sensor_file}: {e}")
    return None
  
  return None

def read_temp_threaded(device_info, result_queue):
  '''
  Thread worker function to read a single sensor's temperature
  device_info: [sensor_file, type, serial]
  result_queue: queue to store results
  '''
  sensor_file, sensor_type, serial = device_info
  temp = read_ext_temp(sensor_file)
  result_queue.put((serial, sensor_type, temp))

# ════════════════════════════════════════════════════════════════════════════════
# Main loop with fixed-rate sampling (4 samples per second = 250ms interval)
# Read ALL sensors in PARALLEL using threads, send in SINGLE batch
# ════════════════════════════════════════════════════════════════════════════════
SAMPLE_INTERVAL = 0.25  # 250ms for 4 samples/second
last_sample_time = time.time()

try:
  while True:
    current_time_float = time.time()
    time_since_last_sample = current_time_float - last_sample_time
    
    # Only sample if enough time has passed (don't wait if it's already time)
    if time_since_last_sample >= SAMPLE_INTERVAL:
      device, nb_device = getDevices()
      
      # ════════════════════════════════════════════════════════════════════════
      # Parallel sensor reading using threads
      # ════════════════════════════════════════════════════════════════════════
      result_queue = Queue()
      threads = []
      
      # Start a thread for each sensor
      for x in range(0, nb_device):
        t = threading.Thread(
          target=read_temp_threaded,
          args=(device[x], result_queue),
          daemon=True
        )
        t.start()
        threads.append(t)
      
      # Wait for all threads to complete
      for t in threads:
        t.join()
      
      # Collect all readings in a single JSON body
      json_body = []
      current_time_str = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
      
      # Process results from queue
      while not result_queue.empty():
        serial, sensor_type, ext_temp = result_queue.get()
        
        # Skip if temperature reading failed
        if ext_temp is None:
          print(f"[TEMP] [ERROR] Failed to read temperature from {serial}")
          continue
        
        if DEBUG:
          print( "Serial:{0} --  Type:{1} --  Temp C: {2} -- Temp F: {3}".format(serial, sensor_type, ext_temp, convert_to_f(ext_temp)))

        # Add this reading to the batch
        json_body.append({
          "measurement": "temperature",
          "tags": {
              "serial": serial,
              "type": sensor_type
          },
          "time": current_time_str,
          "fields": {
              "value": ext_temp
         }
        })
      
      # Send ALL readings in ONE request
      if INFLUX_ENABLE == 'yes' and len(json_body) > 0:
        try:
          DBconnection.sendJSON(json_body, sensor_type="TEMP", debug=DEBUG)
          if DEBUG:
              print(f"[TEMP] → Sent {len(json_body)} sensor(s) to InfluxDB in single batch")
        except Exception as e:
          # Always print errors even in production mode
          print(f"[TEMP] [ERROR] InfluxDB send failed: {e}")
      
      # Update last sample time (use float time, not string)
      last_sample_time = current_time_float
    else:
      # Not time yet - sleep briefly without busy-waiting
      time.sleep(0.01)  # Check again in 10ms

except KeyboardInterrupt:
  print("[TEMP] [STOP] DS18B20 - User interrupted (Ctrl+C)")
  sys.exit()
