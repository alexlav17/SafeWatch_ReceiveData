#!/usr/bin/env python3
"""
Script de test pour simuler un paquet UDP de l'ESP32 avec tous les capteurs
"""
import socket
import json
import time

# Configuration
RASPBERRY_IP = "127.0.0.1"  # localhost pour test
UDP_PORT = 3333

def send_test_packet():
    # Simuler les données que l'ESP32 envoie
    test_data = {
        "bpm": 72.5,
        "ir": 12450,
        "ecg": 8920,
        "x": 0.123,
        "y": -0.456,
        "z": 0.987
    }
    
    payload = json.dumps(test_data)
    
    # Créer socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Envoyer
    print(f"Envoi du paquet de test vers {RASPBERRY_IP}:{UDP_PORT}")
    print(f"Données: {payload}")
    
    sock.sendto(payload.encode(), (RASPBERRY_IP, UDP_PORT))
    sock.close()
    
    print("✓ Paquet envoyé !")

if __name__ == '__main__':
    print("=== TEST UDP ESP32 ===")
    send_test_packet()
    print("\nVérifiez dans les logs du serveur que toutes les données sont reçues:")
    print("  - bpm, ir, ecg (capteur cardiaque)")
    print("  - x, y, z (accéléromètre)")
