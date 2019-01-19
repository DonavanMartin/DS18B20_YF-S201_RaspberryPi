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

## DS18B20
You can install DS18B20 via this command line:<br>
`
$ cd DS18B20/ && bash install.sh
`
You can test with this command <br>
`
$ cat /sys/bus/w1/devices/28-XXXXXXXXXXXX/w1_slave
`

## InfluxDB

`
$ cd InfluxDB/ && bash install.sh
`
You should be able to open: http://<ip>:8083<br>
