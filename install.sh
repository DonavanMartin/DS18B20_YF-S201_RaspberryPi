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

sudo cp rc.local /etc/rc.local
sudo chmod +x /etc/rc.local
sudo systemctl status rc-local
sudo systemctl enable rc-local
sudo systemctl start rc-local