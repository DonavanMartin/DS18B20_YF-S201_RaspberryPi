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
  Read temperature from DS18B20 thermometer
  '''
  f = open(sensor_file, 'r')
  lines = f.readlines()  # Read only first sample in the file
  f.close()
  temp_line = [l for l in lines if 't=' in l]
  ext_temp_c_raw = temp_line[0].replace('=', ' ').split()[-1]
  return convert_from_raw(ext_temp_c_raw)

try:
  while True:
    time.sleep(1)  # Do not oversample (disk space constraint)
    device, nb_device = getDevices()
    for x in range(0, nb_device):
        ext_temp = read_ext_temp(device[x][0])
        if DEBUG:
          print( "Serial:{0} --  Type:{1} --  Temp C: {2} -- Temp F: {3}".format(device[x][2], device[x][1], ext_temp, convert_to_f(ext_temp)))

        if INFLUX_ENABLE == 'yes':
          try:
            # Format JSON for sending to InfluxDB
            current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            json_body = [{
              "measurement": "temperature",
              "tags": {
                  "serial": device[x][2],
                  "type": device[x][1]
              },
              "time": current_time,
              "fields": {
                  "value": ext_temp
             }
            }]

            # Send data to InfluxDB
            DBconnection.sendJSON(json_body, sensor_type="TEMP", debug=DEBUG)
            if DEBUG:
                print(f"[TEMP] → Sent to InfluxDB for {device[x][2]}")
          except Exception as e:
            # Always print errors even in production mode
            print(f"[TEMP] [ERROR] InfluxDB send failed: {e}")

except KeyboardInterrupt:
  print("[TEMP] [STOP] DS18B20 - User interrupted (Ctrl+C)")
  sys.exit()
