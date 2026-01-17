#!/usr/bin/env python3
"""Test simple d'envoi UDP"""
import socket
import json

# Créer le paquet
packet = {
    "ecg": 2450,
    "bpm": 72,
    "x": 0.145,
    "y": -0.023,
    "z": 0.987
}

# Envoyer via UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
json_data = json.dumps(packet)
sock.sendto(json_data.encode('utf-8'), ('localhost', 3333))
sock.close()

print(f"✅ Paquet envoyé: {json_data}")
