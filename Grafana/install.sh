#!/bin/bash
wget https://dl.grafana.com/oss/release/grafana-rpi_9.4.7_armhf.deb
sudo dpkg -i grafana-rpi_9.4.7_armhf.deb
sudo systemctl daemon-reload
sudo systemctl enable grafana-server
sudo systemctl start grafana-server

# Tips & Warnings for Pi Zero
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
# Make permanent: echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab