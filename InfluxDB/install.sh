#!/bin/bash
curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -
source /etc/os-release
test $VERSION_ID = "7" && echo "deb https://repos.influxdata.com/debian wheezy stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
test $VERSION_ID = "8" && echo "deb https://repos.influxdata.com/debian jessie stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
sudo apt-get update && sudo apt-get install influxdb
sudo systemctl start influxdb
sudo netstat -naptu | grep LISTEN | grep influxd
curl -G 'http://localhost:8086/query?pretty=true' --data-urlencode "q=SHOW DATABASES"
sudo systemctl restart influxdb

