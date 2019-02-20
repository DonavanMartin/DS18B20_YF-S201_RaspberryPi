from ConfigParser import SafeConfigParser
from influxdb import InfluxDBClient

INFLUX_URL = 'localhost'
INFLUX_USER = 'admin'
INFLUX_PASS = 'misericorde'
INFLUX_DB = 'measures'
INFLUX_PORT = '8086'

idb_client = InfluxDBClient(INFLUX_URL, INFLUX_PORT, INFLUX_USER, INFLUX_PASS, INFLUX_DB)
print('InfluxDB connection: OK')

def sendJSON(json):
    idb_client.write_points(json)
