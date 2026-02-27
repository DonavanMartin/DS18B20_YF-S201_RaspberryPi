sudo apt-get install -y python3-pip
sudo apt-get install adduser libfontconfig

sudo pip install --break-system-packages influxdb
sudo pip install --break-system-packages influx-client

cd DS18B20 
bash install.sh
# cd ../YF-S201
# bash install.sh
cd ../Grafana
bash install.sh
cd ../InfluxDB
bash install.sh

# InfluxDB can be slow to start on Pi Zero, so we increase the timeout to avoid systemd killing it prematurely
sudo mkdir -p /etc/systemd/system/influxdb.service.d && echo -e "[Service]\nTimeoutStartSec=300" | sudo tee /etc/systemd/system/influxdb.service.d/timeout.conf >/dev/null && sudo systemctl daemon-reload

sudo cp rc.local /etc/rc.local
sudo chmod +x /etc/rc.local
sudo systemctl status rc-local
sudo systemctl enable rc-local
sudo systemctl start rc-local