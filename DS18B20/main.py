#!/usr/bin/env python
import os
import glob
import time
import sys
from datetime import datetime
from datetime import timezone

# Enable line buffering for immediate console output
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1)

os.system('modprobe w1-gpio')
#os.system('modprobe w1-therm')

# Database Connection
scriptPath = os.path.realpath(os.path.dirname(sys.argv[0]))
os.chdir(scriptPath)
sys.path.append("../InfluxDB")
import DBconnection
INFLUX_ENABLE = 'yes'

# Each DS18B20 sensor has a hashed directory
def getDevices():
  base_dir = '/sys/bus/w1/devices/'
  device_folder = glob.glob(base_dir + '28*')
  nb_device = len(device_folder)
  print("Number of devices: {0}".format(nb_device))

  # Create a list containing device info: ['Directory folder', "type", "serial"]
  device = [[0 for x in range(3)] for y in range(nb_device)]
  for x in range(0,nb_device):
    device[x][0] = device_folder[x] + '/w1_slave'
    device[x][1] = "Temperature"
    device[x][2] = device_folder[x].replace(base_dir, '')
#    print(device[x][0])
#    print(device[x][1])
    print(device[x][2])  
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
        print( "Serial:{0} --  Type:{1} --  Temp C: {2} -- Temp F: {3}".format(device[x][2], device[x][1], ext_temp, convert_to_f(ext_temp)))

        if INFLUX_ENABLE == 'yes':
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
          DBconnection.sendJSON(json_body)

except KeyboardInterrupt:
  print("Program terminated")
  sys.exit()
