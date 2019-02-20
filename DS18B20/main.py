#!/usr/bin/env python
import os
import glob
import time
import sys
from datetime import datetime
import os
os.system('modprobe w1-gpio')
#os.system('modprobe w1-therm')

#DBConnection
scriptPath = os.path.realpath(os.path.dirname(sys.argv[0]))
os.chdir(scriptPath)
sys.path.append("../InfluxDB")
import DBconnection
INFLUX_ENABLE = 'yes'

# Each DS18B20 sensor have a directory hashed directory
def getDevices():
  base_dir = '/sys/bus/w1/devices/'
  device_folder = glob.glob(base_dir + '28*')
  nb_device = len(device_folder)
  print("Number of devives: {0}".format(nb_device))

  # Creates a list containing device list with  ['Directory folder, "type", "serial"]
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
  Convert raw millidegrees to standard decimal
  '''
  _raw = float(raw) / 1000.0
  return _raw

def convert_to_f(temp_c):
  '''
  Convert Celcius to Fahrenheit
  '''
  return temp_c * 9.0 / 5.0 + 32.0

def read_ext_temp(sensor_file):
  '''
  Read temps from DS18B20 thermometer
  '''
  f = open(sensor_file, 'r')
  lines = f.readlines() # Read only first sample in the file. 
  f.close()
  temp_line = [l for l in lines if 't=' in l]
  ext_temp_c_raw = temp_line[0].replace('=', ' ').split()[-1]
  return convert_from_raw(ext_temp_c_raw)

try:
  while True:
    time.sleep(1) # Do not oversample (disk space constraint)
    device,nb_device = getDevices()
    for x in range(0,nb_device):
        ext_temp = read_ext_temp(device[x][0])
        print( "Serial:{0} --  Type:{1} --  Temp C: {2} -- Temp F: {3}".format(device[x][2],device[x][1],ext_temp, convert_to_f(ext_temp)))

        if INFLUX_ENABLE == 'yes':
          # Format JSON for sending to InfluxDB
          current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
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
  print("Terminating program")
  sys.exit()
