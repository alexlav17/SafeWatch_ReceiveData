#!/usr/bin/env python3
"""
Script de démarrage du système ESP32 Multi-Capteurs
Lance le serveur Flask avec le bridge UDP intégré
"""
import sys
import os

# Ajouter le répertoire au path
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, Response
from src.api.routes import api_bp
from src.receive import receive_data
from src.ui import INDEX_HTML
from src import udp_bridge

app = Flask(__name__)
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def index():
    return INDEX_HTML

@app.route('/events')
def events():
    return Response(
        receive_data(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )

if __name__ == '__main__':
    print("╔═══════════════════════════════════════════╗")
    print("║   ESP32 MULTI-CAPTEURS - SERVEUR WEB     ║")
    print("╚═══════════════════════════════════════════╝")
    print()
    print("🔧 Initialisation...")
    
    # Démarrer le bridge UDP
    print(f"📡 Démarrage du bridge UDP sur port {udp_bridge.LISTEN_PORT}...")
    udp_bridge.start_udp_bridge()
    print("   ✅ Bridge UDP actif")
    
    # Obtenir l'IP locale
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print()
    print("✨ Serveur prêt !")
    print()
    print("📊 Interface web disponible sur:")
    print(f"   → http://localhost:5000")
    print(f"   → http://{local_ip}:5000")
    print()
    print("📡 ESP32 doit envoyer vers:")
    print(f"   → IP: {local_ip}")
    print(f"   → Port: {udp_bridge.LISTEN_PORT}")
    print(f"   → Protocole: UDP")
    print()
    print("🎯 Données attendues (JSON):")
    print('   {"bpm":72.5,"ir":12450,"ecg":8920,"x":0.12,"y":-0.45,"z":0.98}')
    print()
    print("🔍 Pour tester localement: python3 test_udp.py")
    print()
    print("═" * 50)
    print()
    
    # Lancer le serveur Flask
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,  # Mettre True pour le développement
        threaded=True
    )
