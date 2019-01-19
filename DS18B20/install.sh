#!/bin/bash
echo 'dtoverlay=w1-gpio,gpiopin=4' | sudo tee -a /boot/config.txt
# Please reboot your system! 
