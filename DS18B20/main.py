#!/usr/bin/env python

import os
import glob
import time
import sys
from datetime import datetime
from ConfigParser import SafeConfigParser

CONFIG = 'ds18b20.ini'
INFLUX_ENABLE = 'no'
INFLUX_URL = ''
INFLUX_USER = ''
INFLUX_PASS = ''
INFLUX_DB = ''
INFLUX_PORT = ''

cfg = SafeConfigParser({
  'influxdb_enable': INFLUX_ENABLE,
  'influxdb_url': INFLUX_URL,
  'influxdb_user': INFLUX_USER,
  'influxdb_pass': INFLUX_PASS,
  'influxdb_db': INFLUX_DB,
  'influxdb_port': INFLUX_PORT
  })

cfg.read(CONFIG)
INFLUX_ENABLE = cfg.get('influxdb', 'influxdb_enable')
INFLUX_URL = cfg.get('influxdb', 'influxdb_url')
INFLUX_USER = cfg.get('influxdb', 'influxdb_user')
INFLUX_PASS = cfg.get('influxdb', 'influxdb_pass')
INFLUX_DB = cfg.get('influxdb', 'influxdb_db')
INFLUX_PORT = cfg.get('influxdb', 'influxdb_port')

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

if INFLUX_ENABLE == 'yes':
  from influxdb import InfluxDBClient
  idb_client = InfluxDBClient(INFLUX_URL, INFLUX_PORT, INFLUX_USER, INFLUX_PASS, INFLUX_DB)

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

def read_ext_temp():
  '''
  Read temps from DS18B20 thermometer
  '''
  f = open(device_file, 'r')
  lines = f.readlines()
  f.close()
  temp_line = [l for l in lines if 't=' in l]
  ext_temp_c_raw = temp_line[0].replace('=', ' ').split()[-1]
  return convert_from_raw(ext_temp_c_raw)

try:
  while True:
    ext_temp = read_ext_temp()
    print "EXTERNAL: Temp C: {0} - Temp F: {1}".format(ext_temp, convert_to_f(ext_temp))

    if INFLUX_ENABLE == 'yes':
      # Format JSON for sending to InfluxDB
      current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
      json_body = [{
        "measurement": "temperature",
        "tags": {
            "sensor": "TODO",
            "type": "TODO"
        },
        "time": current_time,
        "fields": {
            "value": ext_temp
        }
      }]

      # Send data to InfluxDB
      idb_client.write_points(json_body)

    # Take a nap for a sec
    time.sleep(1)
except KeyboardInterrupt:
  print "Terminating program"
  sys.exit()
