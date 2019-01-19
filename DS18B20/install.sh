#!/bin/bash
echo 'dtoverlay=w1–gpio' | sudo tee -a /boot/config.txt
sudo pip install influxdb
sudo pip install influx-client
# Please reboot your system! 
