#!/bin/bash
sudo apt-get install adduser libfontconfig
curl -L https://dl.bintray.com/fg2it/deb-rpi-1b/main/g/grafana_4.0.2-1481228314_armhf.deb -o /tmp/grafana_4.0.2-1481228314_armhf.deb
sudo dpkg -i /tmp/grafana_4.0.2-1481228314_armhf.deb
sudo systemctl daemon-reload
sudo systemctl enable grafana-server && sudo systemctl start grafana-server
