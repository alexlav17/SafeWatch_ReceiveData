#!/bin/bash
# Script de démarrage du serveur ESP32 Multi-Capteurs
# Lance le serveur en affichant les logs

cd "$(dirname "$0")"

echo "🚀 Démarrage du serveur ESP32 Multi-Capteurs..."
echo ""

# Tuer les anciens processus
pkill -f "python.*start_server" 2>/dev/null
sleep 1

# Lancer le serveur
python3 start_server.py 2>&1 | tee server.log
