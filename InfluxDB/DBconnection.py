# -*- coding: utf-8 -*-
"""
Connexion et écriture vers InfluxDB 1.8 (compatible Raspberry Pi Zero 32-bit)
Utilise la bibliothèque influxdb-python (pip install influxdb)
"""

from influxdb import InfluxDBClient
import datetime

# ────────────────────────────────────────────────
# CONFIGURATION – À PERSONNALISER
# ────────────────────────────────────────────────
INFLUX_HOST = "localhost"          # ou l'IP du Pi si distant
INFLUX_PORT = 8086
INFLUX_USER = "admin"              # utilisateur créé dans InfluxDB 1.8
INFLUX_PASS = "misericorde"        # mot de passe (change-le !)
INFLUX_DB   = "mesures"            # nom de la base (database)

# ────────────────────────────────────────────────
# Création du client
# ────────────────────────────────────────────────
client = InfluxDBClient(
    host=INFLUX_HOST,
    port=INFLUX_PORT,
    username=INFLUX_USER,
    password=INFLUX_PASS,
    database=INFLUX_DB,
    timeout=10000  # 10 secondes
)

print(f"Connexion InfluxDB 1.8 : OK → database '{INFLUX_DB}'")

def sendJSON(json_data):
    """
    Envoie des points de données à InfluxDB 1.8.
    Accepte exactement le même format que ton ancien code :
    - Une liste de dictionnaires
    - Un seul dictionnaire

    Format attendu :
    [
        {
            "measurement": "temperature",
            "tags": {"room": "salon", "sensor": "temp01"},
            "fields": {"value": 22.5, "humidity": 48.3},
            "time": datetime.datetime.utcnow()   # optionnel (sinon now())
        },
        ...
    ]
    """
    try:
        # Si c'est un seul dict → on le met dans une liste
        if isinstance(json_data, dict):
            json_data = [json_data]

        if not isinstance(json_data, list):
            raise ValueError("Format attendu : dict ou list[dict]")

        # Format compatible write_points (InfluxDB 1.x)
        points = []
        for item in json_data:
            point = {
                "measurement": item["measurement"],
                "tags": item.get("tags", {}),
                "fields": item.get("fields", {}),
            }
            # Timestamp optionnel
            if "time" in item:
                point["time"] = item["time"]
            points.append(point)

        # Écriture
        client.write_points(points)
        print(f"Écriture réussie : {len(points)} point(s) envoyés vers '{INFLUX_DB}'")

    except Exception as e:
        print(f"Erreur lors de l'envoi vers InfluxDB 1.8 : {e}")
        # Tu peux ajouter ici du retry, du logging, etc.


# ────────────────────────────────────────────────
# Exemple d'utilisation (identique à ton ancien format)
# ────────────────────────────────────────────────
if __name__ == "__main__":
    # Exemple avec plusieurs mesures
    data = [
        {
            "measurement": "temperature",
            "tags": {"room": "salon", "sensor": "temp01"},
            "fields": {"value": 22.5, "humidity": 48.3},
            "time": datetime.datetime.utcnow()
        },
        {
            "measurement": "flow",
            "tags": {"sensor": "YF-S201", "location": "eau froide"},
            "fields": {"debit_l_min": 3.8, "total_l": 1452.7}
        },
        {
            "measurement": "onewire",
            "tags": {"device": "DS18B20", "id": "28-01123456789a"},
            "fields": {"temperature": 19.4}
        }
    ]

    sendJSON(data)

    # Exemple avec un seul point
    single = {
        "measurement": "cpu",
        "tags": {"host": "raspberrypi-zero"},
        "fields": {"usage": 12.3}
    }
    sendJSON(single)

    # Bonne pratique : fermer la connexion à la fin du programme
    # client.close()  # décommente si tu as plusieurs sessions