#!/usr/bin/env bash
set -euo pipefail

echo "=== InfluxDB 1.8 Installation on Raspberry Pi Zero (32-bit) ==="

# 1. Minimal dependencies (likely already installed)
echo "→ Installing base tools if missing"
sudo apt update
sudo apt install -y curl gnupg ca-certificates lsb-release

# 2. GPG Key (compatible version for legacy OS and 32-bit)
echo "→ Adding official GPG key (legacy compatibility)"
curl -fsSL https://repos.influxdata.com/influxdata-archive_compat.key \
  | gpg --dearmor \
  | sudo tee /etc/apt/keyrings/influxdata-archive_compat.gpg > /dev/null

# 3. Add repository (using your distribution codename to avoid issues)
CODENAME=$(lsb_release -cs)   # example: bookworm, trixie, etc.
echo "→ Adding InfluxDB 1.x repository for ${CODENAME}"
echo "deb [signed-by=/etc/apt/keyrings/influxdata-archive_compat.gpg] https://repos.influxdata.com/debian ${CODENAME} stable" \
  | sudo tee /etc/apt/sources.list.d/influxdb.list

# 4. Update and installation (InfluxDB only, no unnecessary dependencies)
echo "→ Updating package list and installing InfluxDB 1.8"
sudo apt update
sudo apt install -y influxdb

# 5. Service startup and enable
echo "→ Enabling and starting the service"
sudo systemctl daemon-reload
sudo systemctl unmask influxdb   # au cas où masked
sudo systemctl enable influxdb
sudo systemctl start influxdb

# Short wait (service is lightweight on Pi Zero)
sleep 8

# 6. Quick verifications
echo "→ Verifying the service is running"
sudo systemctl status influxdb --no-pager | head -n 15

echo "→ Checking port 8086"
sudo ss -tuln | grep 8086 || echo "→ Port 8086 not detected – check logs"

echo "→ Creating 'measures' database (if it doesn't exist)"
curl -G 'http://localhost:8086/query' --data-urlencode "q=CREATE DATABASE mesures" || true

echo ""
echo "=============================================================="
echo "InfluxDB 1.8 should be installed and operational!"
echo ""
echo "Next quick steps:"
echo "  1. Create a user (if not already done):"
echo "     influx"
echo "     CREATE USER admin WITH PASSWORD 'misericorde' WITH ALL PRIVILEGES"
echo ""
echo "  2. Test a simple write:"
echo "     curl -i -XPOST 'http://localhost:8086/write?db=mesures' --data-binary 'test,location=salon value=42'"
echo ""
echo "  3. Your Python code with influxdb-python works directly:"
echo "     InfluxDBClient('localhost', 8086, 'admin', 'misericorde', 'mesures')"
echo ""
echo "Detailed logs if needed: journalctl -u influxdb -n 50"
echo "Good luck with your sensors!"
echo "=============================================================="


echo "→ Installing Chronograf on port 8888"
wget https://dl.influxdata.com/chronograf/releases/chronograf_1.10.5_armhf.deb   # latest 1.x version compatible with armhf in 2026
sudo dpkg -i chronograf_1.10.5_armhf.deb
sudo apt install -f   # fixes dependencies if needed
sudo systemctl enable chronograf
sudo systemctl start chronograf