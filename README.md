# DS18B20_RaspberryPi
The DS18B20 project can be use as a RaspberryPi temperature sensor example. 

## Installation
1. Install the project libraries
`xargs sudo apt install <libraries.txt`

2. Install the python requirements
`pip3 install -r requirements.txt`

## PiOLED
You can install PiOLED via this command line:<br>
`
$ cd PiOLED/ && bash install.sh
`
<br>For testing, see examples in folder:<br>
`
$ ls Adafruit_Python_SSD1306/examples
`

## DS18B20
You can install DS18B20 via this command line:<br>
`
$ cd DS18B20/ && bash install.sh
`
<br>You can test with this command:<br>
`
$ cat /sys/bus/w1/devices/28-XXXXXXXXXXXX/w1_slave
`

## InfluxDB
You can install InfluxDB via this command line:<br>
`
$ cd InfluxDB/ && bash install.sh
`
<br>You should be now able to open:<br>
http://localhost:8083<br>
