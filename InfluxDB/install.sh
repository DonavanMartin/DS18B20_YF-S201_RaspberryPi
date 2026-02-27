#!/usr/bin/env bash
set -euo pipefail

echo "=== Installation InfluxDB 1.8 sur Raspberry Pi Zero (32-bit) ==="

# 1. Dépendances minimales (déjà probablement installées)
echo "→ Installation des outils de base si absents"
sudo apt update
sudo apt install -y curl gnupg ca-certificates lsb-release

# 2. Clé GPG (version compat pour vieux OS et 32-bit)
echo "→ Ajout de la clé GPG officielle (compatibilité legacy)"
curl -fsSL https://repos.influxdata.com/influxdata-archive_compat.key \
  | gpg --dearmor \
  | sudo tee /etc/apt/keyrings/influxdata-archive_compat.gpg > /dev/null

# 3. Ajout du dépôt (on utilise le codename de ta distribution pour éviter les problèmes)
CODENAME=$(lsb_release -cs)   # ex: bookworm, trixie, etc.
echo "→ Ajout du dépôt InfluxDB 1.x pour ${CODENAME}"
echo "deb [signed-by=/etc/apt/keyrings/influxdata-archive_compat.gpg] https://repos.influxdata.com/debian ${CODENAME} stable" \
  | sudo tee /etc/apt/sources.list.d/influxdb.list

# 4. Mise à jour et installation (seulement influxdb, pas de dépendances inutiles)
echo "→ Mise à jour liste paquets et installation d'InfluxDB 1.8"
sudo apt update
sudo apt install -y influxdb

# 5. Démarrage et activation
echo "→ Activation et démarrage du service"
sudo systemctl daemon-reload
sudo systemctl unmask influxdb   # au cas où masked
sudo systemctl enable influxdb
sudo systemctl start influxdb

# Attente courte (le service est léger sur Pi Zero)
sleep 8

# 6. Vérifications rapides
echo "→ Vérification que le service tourne"
sudo systemctl status influxdb --no-pager | head -n 15

echo "→ Vérification port 8086"
sudo ss -tuln | grep 8086 || echo "→ Port 8086 non détecté – vérifie les logs"

echo "→ Création de la base 'mesures' (si elle n'existe pas déjà)"
curl -G 'http://localhost:8086/query' --data-urlencode "q=CREATE DATABASE mesures" || true

echo ""
echo "=============================================================="
echo "InfluxDB 1.8 devrait être installé et opérationnel !"
echo ""
echo "Prochaines étapes rapides :"
echo "  1. Créer un utilisateur (si pas déjà fait) :"
echo "     influx"
echo "     CREATE USER admin WITH PASSWORD 'misericorde' WITH ALL PRIVILEGES"
echo ""
echo "  2. Tester une écriture simple :"
echo "     curl -i -XPOST 'http://localhost:8086/write?db=mesures' --data-binary 'test,location=salon value=42'"
echo ""
echo "  3. Ton ancien code Python avec influxdb-python marche directement :"
echo "     InfluxDBClient('localhost', 8086, 'admin', 'misericorde', 'mesures')"
echo ""
echo "Logs détaillés si besoin : journalctl -u influxdb -n 50"
echo "Bonne continuation avec tes capteurs !"
echo "=============================================================="


echo "→ Installation de chronograf port 8888"
wget https://dl.influxdata.com/chronograf/releases/chronograf_1.10.5_armhf.deb   # dernière version 1.x compatible armhf en 2026
sudo dpkg -i chronograf_1.10.5_armhf.deb
sudo apt install -f   # corrige dépendances si besoin
sudo systemctl enable chronograf
sudo systemctl start chronograf