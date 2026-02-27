#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulation de 8 capteurs DS18B20 pour tester l'envoi vers InfluxDB 1.8
Génère des températures réalistes (entre 18 et 28 °C) avec légère variation
"""

import time
import random
from datetime import datetime
import sys
import os

# Chemin vers ton module DBconnection
scriptPath = os.path.realpath(os.path.dirname(sys.argv[0]))
os.chdir(scriptPath)
sys.path.append("../InfluxDB")
import DBconnection

INFLUX_ENABLE = 'yes'

# ────────────────────────────────────────────────
# Configuration simulation
# ────────────────────────────────────────────────
NB_DEVICES = 8
BASE_SERIAL = "28-02123456"  # préfixe commun pour les serials simulés

# Plage de températures réalistes pour une pièce (en °C)
TEMP_MIN = 18.0
TEMP_MAX = 28.0

# Variation max par tick (pour simuler évolution naturelle)
VARIATION_MAX = 0.4

# Stockage des températures actuelles (pour évolution progressive)
current_temps = [random.uniform(TEMP_MIN + 2, TEMP_MAX - 2) for _ in range(NB_DEVICES)]

# ────────────────────────────────────────────────
# Génération des "devices" simulés
# ────────────────────────────────────────────────
def getDevices():
    devices = []
    for i in range(NB_DEVICES):
        serial = f"{BASE_SERIAL}{i:02d}"  # ex: 28-0212345600, 28-0212345601, ...
        devices.append({
            "path": f"/sys/bus/w1/devices/{serial}/w1_slave",  # fictif
            "type": "Temperature",
            "serial": serial
        })
    print(f"Simulation de {len(devices)} capteurs DS18B20")
    return devices, len(devices)


# ────────────────────────────────────────────────
# Lecture simulée
# ────────────────────────────────────────────────
def read_ext_temp(device_index):
    # Évolution progressive + petit bruit aléatoire
    current = current_temps[device_index]
    delta = random.uniform(-VARIATION_MAX, VARIATION_MAX)
    new_temp = current + delta
    
    # Contrainte dans la plage réaliste
    new_temp = max(TEMP_MIN, min(TEMP_MAX, new_temp))
    
    current_temps[device_index] = new_temp
    return round(new_temp, 3)


# ────────────────────────────────────────────────
# Boucle principale
# ────────────────────────────────────────────────
try:
    while True:
        time.sleep(1)  # Intervalle de 1 seconde (ajuste selon tes besoins)

        devices, nb_device = getDevices()

        current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        for i in range(nb_device):
            dev = devices[i]
            ext_temp = read_ext_temp(i)

            print(f"Serial: {dev['serial']}  -- Type: {dev['type']}  -- Temp C: {ext_temp:.3f}  -- Temp F: {(ext_temp * 9/5 + 32):.2f}")

            if INFLUX_ENABLE.lower() == 'yes':
                json_body = [{
                    "measurement": "temperature",
                    "tags": {
                        "serial": dev['serial'],
                        "type": dev['type']
                    },
                    "time": current_time,
                    "fields": {
                        "value": ext_temp
                    }
                }]

                try:
                    DBconnection.sendJSON(json_body)
                    print(f"  → Envoyé à InfluxDB pour {dev['serial']}")
                except Exception as e:
                    print(f"  → Erreur envoi InfluxDB : {e}")

except KeyboardInterrupt:
    print("\nArrêt du programme par Ctrl+C")
    sys.exit(0)
except Exception as e:
    print(f"Erreur inattendue : {e}")
    sys.exit(1)