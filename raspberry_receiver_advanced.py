#!/usr/bin/env python3
"""
Récepteur UDP avancé pour ESP32
Compatible avec le nouveau format JSON
- Parse les données capteur cardiaque (signal, BPM)
- Parse les données accéléromètre (X, Y, Z)
- Valide les plages de valeurs
- Affiche les données en temps réel
"""

import socket
import json
import sys
from datetime import datetime


class ESP32Receiver:
    """Récepteur UDP pour ESP32 avec validation des données"""
    
    def __init__(self, host='0.0.0.0', port=3333):
        self.host = host
        self.port = port
        self.sock = None
        self.packet_count = 0
        
    def validate_bpm(self, bpm):
        """Valide que le BPM est dans la plage acceptable (40-180)"""
        if bpm is None:
            return None
        try:
            bpm_val = float(bpm)
            if 40 <= bpm_val <= 180:
                return bpm_val
            return None
        except (ValueError, TypeError):
            return None
    
    def validate_accel(self, value):
        """Valide que l'accélération est dans la plage ±2g"""
        if value is None:
            return 0.0
        try:
            val = float(value)
            # Clamper à ±2g
            return max(-2.0, min(2.0, val))
        except (ValueError, TypeError):
            return 0.0
    
    def parse_packet(self, data):
        """Parse un paquet JSON de l'ESP32"""
        try:
            packet = json.loads(data)
        except json.JSONDecodeError as e:
            print(f"❌ Erreur JSON: {e}")
            return None
        
        # Extraction et validation des champs
        timestamp = packet.get('timestamp', datetime.now().isoformat())
        
        # Signal ECG
        ecg = packet.get('ecg')
        if ecg is not None:
            try:
                ecg = int(ecg)
            except (ValueError, TypeError):
                ecg = None
        
        # BPM
        bpm = self.validate_bpm(packet.get('bpm'))
        
        # Accéléromètre
        accel_x = self.validate_accel(packet.get('x', 0))
        accel_y = self.validate_accel(packet.get('y', 0))
        accel_z = self.validate_accel(packet.get('z', 0))
        
        return {
            'timestamp': timestamp,
            'ecg': ecg,
            'bpm': bpm,
            'accel': {
                'x': round(accel_x, 3),
                'y': round(accel_y, 3),
                'z': round(accel_z, 3)
            },
            'raw': packet
        }
    
    def format_display(self, data):
        """Formate les données pour l'affichage console"""
        if not data:
            return ""
        
        bpm_str = f"{data['bpm']:.0f}" if data['bpm'] else "--"
        ecg_str = f"{data['ecg']}" if data['ecg'] is not None else "----"
        
        accel = data['accel']
        
        return (
            f"[{self.packet_count:05d}] "
            f"❤️  BPM: {bpm_str:>3} | "
            f"📊 ECG: {ecg_str:>4} | "
            f"📐 Accel: X={accel['x']:>6.3f}g  Y={accel['y']:>6.3f}g  Z={accel['z']:>6.3f}g"
        )
    
    def start(self):
        """Démarre l'écoute UDP"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.host, self.port))
            
            print("\n" + "="*80)
            print("🚀 ESP32 RECEIVER - Mode Avancé")
            print("="*80)
            print(f"📡 Écoute UDP sur {self.host}:{self.port}")
            print(f"📊 Validation: BPM [40-180], ECG [brut], Accel [±2.0g]")
            print(f"⏱️  Fréquence attendue: 10Hz (100ms entre paquets)")
            print("="*80)
            print()
            
            while True:
                try:
                    data, addr = self.sock.recvfrom(4096)
                    raw_data = data.decode('utf-8').strip()
                    
                    # Parser le paquet
                    parsed = self.parse_packet(raw_data)
                    
                    if parsed:
                        self.packet_count += 1
                        
                        # Afficher les données
                        print(self.format_display(parsed))
                        
                        # Afficher JSON brut tous les 50 paquets
                        if self.packet_count % 50 == 0:
                            print(f"\n📦 Paquet brut #{self.packet_count}:")
                            print(json.dumps(parsed['raw'], indent=2))
                            print()
                    else:
                        print(f"⚠️  Paquet invalide reçu de {addr}")
                
                except KeyboardInterrupt:
                    print("\n\n⏹️  Arrêt demandé par l'utilisateur")
                    break
                except Exception as e:
                    print(f"❌ Erreur: {e}")
                    continue
        
        finally:
            if self.sock:
                self.sock.close()
            print(f"\n✅ Session terminée. Total paquets reçus: {self.packet_count}")


def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Récepteur UDP ESP32 avancé')
    parser.add_argument('--host', default='0.0.0.0', help='Adresse d\'écoute (défaut: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=3333, help='Port d\'écoute (défaut: 3333)')
    
    args = parser.parse_args()
    
    receiver = ESP32Receiver(host=args.host, port=args.port)
    receiver.start()


if __name__ == '__main__':
    main()
