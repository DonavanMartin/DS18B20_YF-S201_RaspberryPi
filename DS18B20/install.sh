#!/bin/bash

# Determine correct boot config path (modern systems use /boot/firmware/)
if [ -f /boot/firmware/config.txt ]; then
  CONFIG_FILE="/boot/firmware/config.txt"
elif [ -f /boot/firmware/config.txt ]; then
  CONFIG_FILE="/boot/firmware/config.txt"
else
  echo "[ERROR] config.txt not found in /boot/ or /boot/firmware/"
  exit 1
fi

echo "[INFO] Using config file: $CONFIG_FILE"

# Check if overlay already exists before adding
if grep -q "dtoverlay=w1-gpio,gpiopin=4" "$CONFIG_FILE"; then
  echo "[INFO] w1-gpio overlay already present in $CONFIG_FILE"
else
  echo "[INFO] Adding w1-gpio overlay to $CONFIG_FILE"
  echo 'dtoverlay=w1-gpio,gpiopin=4' | sudo tee -a "$CONFIG_FILE"
fi

# Add w1-gpio to modules if not already present
if grep -q "w1-gpio" /etc/modules; then
  echo "[INFO] w1-gpio already in /etc/modules"
else
  echo "[INFO] Adding w1-gpio to /etc/modules"
  echo 'w1-gpio' | sudo tee -a /etc/modules
fi

echo "[INFO] Loading w1-gpio driver..."
sudo modprobe w1-gpio

echo "[SUCCESS] DS18B20 installation complete"
echo "[NOTE] Configuration will take effect after reboot: sudo reboot"