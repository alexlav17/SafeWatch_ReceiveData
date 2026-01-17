#!/usr/bin/env python3
"""
Simulateur ESP32 pour tester le système sans matériel
Envoie des paquets UDP simulés au serveur flask_app.py
"""

import socket
import json
import time
import random
import math
import argparse
from datetime import datetime


class ESP32Simulator:
    """Simule un ESP32 envoyant des données de capteurs"""
    
    def __init__(self, host='localhost', port=3333, frequency=10):
        self.host = host
        self.port = port
        self.interval = 1.0 / frequency  # Intervalle en secondes
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.packet_count = 0
        self.start_time = time.time()
        
    def simulate_heartbeat(self, t):
        """Simule un signal cardiaque réaliste"""
        # Fréquence cardiaque de base (1.2 Hz = 72 BPM)
        heart_freq = 1.2
        
        # Signal sinusoïdal avec harmoniques pour simuler un ECG
        signal = 2500  # Baseline
        signal += 800 * math.sin(2 * math.pi * heart_freq * t)  # Onde principale
        signal += 200 * math.sin(4 * math.pi * heart_freq * t)  # Harmonique
        signal += 100 * math.sin(6 * math.pi * heart_freq * t)  # Harmonique
        
        # Ajouter du bruit
        signal += random.uniform(-50, 50)
        
        # Clamper à la plage ADC
        signal = max(200, min(3500, int(signal)))
        
        # Calculer le BPM (avec petite variation)
        bpm = int(72 + random.uniform(-3, 3))
        
        return signal, bpm
    
    def simulate_accelerometer(self, t):
        """Simule un accéléromètre avec mouvement"""
        # Simuler un mouvement de marche/course
        walk_freq = 2.0  # 2 Hz = 120 pas/minute
        
        # X : mouvement avant-arrière
        x = 0.3 * math.sin(2 * math.pi * walk_freq * t)
        
        # Y : mouvement latéral
        y = 0.2 * math.sin(2 * math.pi * walk_freq * t + math.pi / 2)
        
        # Z : mouvement vertical (gravité + oscillations)
        z = 1.0 + 0.15 * math.sin(2 * math.pi * walk_freq * t)
        
        # Ajouter du bruit
        x += random.uniform(-0.02, 0.02)
        y += random.uniform(-0.02, 0.02)
        z += random.uniform(-0.02, 0.02)
        
        # Clamper à ±2g
        x = max(-2.0, min(2.0, x))
        y = max(-2.0, min(2.0, y))
        z = max(-2.0, min(2.0, z))
        
        return round(x, 3), round(y, 3), round(z, 3)
    
    def generate_packet(self):
        """Génère un paquet de données simulé"""
        t = time.time() - self.start_time
        
        # Générer les valeurs
        ecg, bpm = self.simulate_heartbeat(t)
        accel_x, accel_y, accel_z = self.simulate_accelerometer(t)
        
        # Créer le paquet JSON
        packet = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'ecg': ecg,
            'bpm': bpm,
            'x': accel_x,
            'y': accel_y,
            'z': accel_z
        }
        
        return packet
    
    def send_packet(self, packet):
        """Envoie un paquet UDP"""
        json_data = json.dumps(packet)
        self.sock.sendto(json_data.encode('utf-8'), (self.host, self.port))
        self.packet_count += 1
        
        return len(json_data)
    
    def run(self, duration=None):
        """Lance la simulation"""
        print("\n" + "="*70)
        print("🎭 SIMULATEUR ESP32")
        print("="*70)
        print(f"📡 Cible: {self.host}:{self.port}")
        print(f"⏱️  Fréquence: {1/self.interval:.1f} Hz")
        if duration:
            print(f"⏰ Durée: {duration} secondes")
        else:
            print(f"⏰ Durée: Infinie (Ctrl+C pour arrêter)")
        print("="*70)
        print()
        
        start = time.time()
        next_send = start
        
        try:
            while True:
                current_time = time.time()
                
                # Vérifier la durée limite
                if duration and (current_time - start) >= duration:
                    break
                
                # Attendre le prochain envoi
                if current_time >= next_send:
                    # Générer et envoyer le paquet
                    packet = self.generate_packet()
                    size = self.send_packet(packet)
                    
                    # Afficher tous les 10 paquets
                    if self.packet_count % 10 == 0:
                        elapsed = current_time - start
                        rate = self.packet_count / elapsed if elapsed > 0 else 0
                        
                        print(f"[{self.packet_count:05d}] "
                              f"❤️ BPM:{packet['bpm']:3d} | "
                              f"📊 ECG:{packet['ecg']:4d} | "
                              f"📐 X:{packet['x']:6.3f} Y:{packet['y']:6.3f} Z:{packet['z']:6.3f} | "
                              f"⚡ {rate:.1f} pkt/s")
                    
                    # Afficher le JSON tous les 50 paquets
                    if self.packet_count % 50 == 0:
                        print(f"\n📦 Paquet JSON #{self.packet_count}:")
                        print(json.dumps(packet, indent=2))
                        print()
                    
                    # Planifier le prochain envoi
                    next_send += self.interval
                else:
                    # Petite pause pour ne pas consommer trop de CPU
                    time.sleep(0.001)
        
        except KeyboardInterrupt:
            print("\n\n⏹️  Arrêt demandé par l'utilisateur")
        
        finally:
            elapsed = time.time() - start
            avg_rate = self.packet_count / elapsed if elapsed > 0 else 0
            
            print("\n" + "="*70)
            print("📊 STATISTIQUES")
            print("="*70)
            print(f"Total paquets envoyés: {self.packet_count}")
            print(f"Durée: {elapsed:.1f} secondes")
            print(f"Taux moyen: {avg_rate:.2f} paquets/seconde")
            print(f"Taux théorique: {1/self.interval:.2f} paquets/seconde")
            print("="*70)
            
            self.sock.close()


def main():
    parser = argparse.ArgumentParser(
        description='Simulateur ESP32 pour tester le système de monitoring'
    )
    parser.add_argument(
        '--host',
        default='localhost',
        help='Adresse du serveur (défaut: localhost)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=3333,
        help='Port UDP du serveur (défaut: 3333)'
    )
    parser.add_argument(
        '--frequency',
        type=int,
        default=10,
        help='Fréquence d\'envoi en Hz (défaut: 10)'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=None,
        help='Durée de la simulation en secondes (défaut: infini)'
    )
    
    args = parser.parse_args()
    
    # Créer et lancer le simulateur
    sim = ESP32Simulator(
        host=args.host,
        port=args.port,
        frequency=args.frequency
    )
    sim.run(duration=args.duration)


if __name__ == '__main__':
    main()
