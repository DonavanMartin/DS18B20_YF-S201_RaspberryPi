#!/bin/bash
echo 'dtoverlay=w1-gpio,gpiopin=4' | sudo tee -a /boot/config.txt
echo 'w1-gpio' | sudo tee -a /etc/modules
#echo 'w1-therm' | sudo tee -a /etc/modules
sudo modprobe w1-gpio
#sudo modprobe w1-therm