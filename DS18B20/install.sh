#!/bin/bash
echo 'dtoverlay=w1-gpio,gpiopin=4' | sudo tee -a /boot/config.txt
sudo pip install influxdb
sudo pip install influx-client
# Please reboot your system! 
