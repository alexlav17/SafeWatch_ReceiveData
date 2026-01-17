#!/bin/bash

# Script de lancement rapide ESP32 Monitor
# Usage: ./quick_start.sh

echo "╔═══════════════════════════════════════════╗"
echo "║   ESP32 MONITOR - Démarrage Rapide       ║"
echo "╚═══════════════════════════════════════════╝"
echo ""

# Vérifier si on est dans le bon répertoire
if [ ! -f "flask_app.py" ]; then
    echo "❌ Erreur: flask_app.py non trouvé"
    echo "   Veuillez exécuter ce script depuis le dossier esp32-listener"
    exit 1
fi

# Vérifier Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

echo "🔍 Vérification de l'environnement..."

# Vérifier si venv existe
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
    echo "   ✅ Environnement virtuel créé"
fi

# Activer l'environnement virtuel
echo "🔌 Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer/mettre à jour les dépendances
echo "📥 Installation des dépendances..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Erreur lors de l'installation des dépendances"
    exit 1
fi

echo "   ✅ Dépendances installées"
echo ""

# Obtenir l'IP locale
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo "═══════════════════════════════════════════"
echo "🚀 Démarrage du serveur ESP32 Monitor..."
echo "═══════════════════════════════════════════"
echo ""
echo "📡 Interface web disponible sur :"
echo "   • Local:  http://localhost:5000"
echo "   • Réseau: http://$LOCAL_IP:5000"
echo ""
echo "📡 Serveur UDP en écoute sur port 3333"
echo ""
echo "💡 Appuyez sur Ctrl+C pour arrêter le serveur"
echo ""
echo "═══════════════════════════════════════════"
echo ""

# Lancer l'application
python3 flask_app.py
