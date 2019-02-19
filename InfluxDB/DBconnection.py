
from ConfigParser import SafeConfigParser
from influxdb import InfluxDBClient

CONFIG = 'ds18b20.ini'
INFLUX_URL = ''
INFLUX_USER = ''
INFLUX_PASS = ''
INFLUX_DB = ''
INFLUX_PORT = ''

cfg = SafeConfigParser({
  'influxdb_url': INFLUX_URL,
  'influxdb_user': INFLUX_USER,
  'influxdb_pass': INFLUX_PASS,
  'influxdb_db': INFLUX_DB,
  'influxdb_port': INFLUX_PORT
  })

cfg.read(CONFIG)
INFLUX_URL = cfg.get('influxdb', 'influxdb_url')
INFLUX_USER = cfg.get('influxdb', 'influxdb_user')
INFLUX_PASS = cfg.get('influxdb', 'influxdb_pass')
INFLUX_DB = cfg.get('influxdb', 'influxdb_db')
INFLUX_PORT = cfg.get('influxdb', 'influxdb_port')

idb_client = InfluxDBClient(INFLUX_URL, INFLUX_PORT, INFLUX_USER, INFLUX_PASS, INFLUX_DB)

def sendJSON(json):
  idb_client.write_points(json)
  return 1
