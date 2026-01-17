#!/usr/bin/env python3
"""
ESP32 Listener - Démarrage Application Principale
Lance flask_app.py (interface WebSocket + Chart.js)
"""
import os
import sys
import subprocess

if __name__ == "__main__":
    # Chemin vers l'application principale
    script_path = os.path.join(os.path.dirname(__file__), 'flask_app.py')
    
    print("\n" + "="*60)
    print("🚀 ESP32 LISTENER - INTERFACE WEB TEMPS RÉEL")
    print("="*60)
    print("📊 Interface: Chart.js (graphique ECG défilant)")
    print("❤️  Affichage: BPM temps réel + accéléromètre")
    print("🔌 Communication: UDP (port 3333) + WebSocket")
    print("📝 Fonctionnalités: Enregistrement CSV")
    print("="*60 + "\n")
    
    # Lancer l'application principale
    subprocess.run([sys.executable, script_path])
