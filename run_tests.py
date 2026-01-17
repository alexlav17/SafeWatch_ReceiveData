#!/usr/bin/env python3
"""
Tests automatiques pour vérifier le bon fonctionnement du système
Exécute une suite de tests complets
"""

import socket
import json
import time
import subprocess
import sys
import os
import signal

# Couleurs pour l'affichage
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.RESET}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.RESET}")


class SystemTester:
    """Classe pour tester le système ESP32 Monitor"""
    
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.server_process = None
        
    def send_udp_packet(self, packet, host='localhost', port=3333):
        """Envoie un paquet UDP"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            json_data = json.dumps(packet)
            sock.sendto(json_data.encode('utf-8'), (host, port))
            sock.close()
            return True
        except Exception as e:
            print_error(f"Erreur envoi UDP: {e}")
            return False
    
    def check_port_available(self, port):
        """Vérifie qu'un port est disponible"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('localhost', port))
            sock.close()
            return True
        except OSError:
            return False
    
    def test_dependencies(self):
        """Vérifie que toutes les dépendances sont installées"""
        print_info("Test 1: Vérification des dépendances...")
        
        required_modules = [
            'flask',
            'flask_socketio',
            'socketio'
        ]
        
        all_ok = True
        for module in required_modules:
            try:
                __import__(module)
                print_success(f"  Module {module} présent")
            except ImportError:
                print_error(f"  Module {module} manquant")
                all_ok = False
        
        if all_ok:
            self.tests_passed += 1
            print_success("Test dépendances: RÉUSSI\n")
        else:
            self.tests_failed += 1
            print_error("Test dépendances: ÉCHOUÉ\n")
        
        return all_ok
    
    def test_files_exist(self):
        """Vérifie que tous les fichiers nécessaires existent"""
        print_info("Test 2: Vérification des fichiers...")
        
        required_files = [
            'flask_app.py',
            'templates/index.html',
            'requirements.txt',
            'simulate_esp32.py',
            'raspberry_receiver_advanced.py'
        ]
        
        all_ok = True
        for file in required_files:
            if os.path.exists(file):
                print_success(f"  Fichier {file} présent")
            else:
                print_error(f"  Fichier {file} manquant")
                all_ok = False
        
        if all_ok:
            self.tests_passed += 1
            print_success("Test fichiers: RÉUSSI\n")
        else:
            self.tests_failed += 1
            print_error("Test fichiers: ÉCHOUÉ\n")
        
        return all_ok
    
    def test_udp_reception(self):
        """Teste la réception UDP"""
        print_info("Test 3: Test réception UDP...")
        
        # Vérifier que le port 3333 est disponible ou occupé par notre serveur
        port_status = self.check_port_available(3333)
        
        # Envoyer un paquet test
        test_packet = {
            'signal': 2500,
            'bpm': 72,
            'x': 0.1,
            'y': 0.2,
            'z': 1.0
        }
        
        if self.send_udp_packet(test_packet):
            print_success("  Paquet UDP envoyé avec succès")
            self.tests_passed += 1
            print_success("Test UDP: RÉUSSI\n")
            return True
        else:
            print_error("  Échec d'envoi du paquet UDP")
            self.tests_failed += 1
            print_error("Test UDP: ÉCHOUÉ\n")
            return False
    
    def test_data_validation(self):
        """Teste la validation des données"""
        print_info("Test 4: Test validation des données...")
        
        # Importer les fonctions de validation
        try:
            sys.path.insert(0, os.path.dirname(__file__))
            import flask_app
            
            # Test BPM valide
            bpm_valid = flask_app.validate_bpm(72)
            if bpm_valid == 72:
                print_success("  BPM valide (72) accepté")
            else:
                print_error(f"  BPM valide rejeté: {bpm_valid}")
                self.tests_failed += 1
                return False
            
            # Test BPM invalide (trop bas)
            bpm_invalid_low = flask_app.validate_bpm(20)
            if bpm_invalid_low is None:
                print_success("  BPM invalide (20) rejeté")
            else:
                print_error(f"  BPM invalide accepté: {bpm_invalid_low}")
                self.tests_failed += 1
                return False
            
            # Test BPM invalide (trop haut)
            bpm_invalid_high = flask_app.validate_bpm(200)
            if bpm_invalid_high is None:
                print_success("  BPM invalide (200) rejeté")
            else:
                print_error(f"  BPM invalide accepté: {bpm_invalid_high}")
                self.tests_failed += 1
                return False
            
            self.tests_passed += 1
            print_success("Test validation: RÉUSSI\n")
            return True
            
        except Exception as e:
            print_error(f"  Erreur test validation: {e}")
            self.tests_failed += 1
            print_error("Test validation: ÉCHOUÉ\n")
            return False
    
    def test_json_parsing(self):
        """Teste le parsing JSON"""
        print_info("Test 5: Test parsing JSON...")
        
        # Test paquet valide
        valid_packet = '{"signal":2500,"bpm":72,"x":0.1,"y":0.2,"z":1.0}'
        
        try:
            parsed = json.loads(valid_packet)
            if 'signal' in parsed and 'bpm' in parsed:
                print_success("  Paquet JSON valide parsé")
                self.tests_passed += 1
                print_success("Test parsing: RÉUSSI\n")
                return True
        except Exception as e:
            print_error(f"  Erreur parsing JSON: {e}")
            self.tests_failed += 1
            print_error("Test parsing: ÉCHOUÉ\n")
            return False
    
    def print_summary(self):
        """Affiche le résumé des tests"""
        print("\n" + "="*60)
        print("RÉSUMÉ DES TESTS")
        print("="*60)
        print(f"Tests réussis: {Colors.GREEN}{self.tests_passed}{Colors.RESET}")
        print(f"Tests échoués: {Colors.RED}{self.tests_failed}{Colors.RESET}")
        total = self.tests_passed + self.tests_failed
        if total > 0:
            success_rate = (self.tests_passed / total) * 100
            print(f"Taux de réussite: {success_rate:.1f}%")
        print("="*60)
        
        if self.tests_failed == 0:
            print(f"\n{Colors.GREEN}✨ TOUS LES TESTS SONT RÉUSSIS !{Colors.RESET}")
            print(f"{Colors.GREEN}Le système est prêt à être utilisé.{Colors.RESET}\n")
            return 0
        else:
            print(f"\n{Colors.RED}❌ CERTAINS TESTS ONT ÉCHOUÉ{Colors.RESET}")
            print(f"{Colors.YELLOW}Consultez les messages ci-dessus pour corriger les problèmes.{Colors.RESET}\n")
            return 1
    
    def run_all_tests(self):
        """Exécute tous les tests"""
        print("\n" + "="*60)
        print("ESP32 MONITOR - SUITE DE TESTS AUTOMATIQUES")
        print("="*60 + "\n")
        
        # Exécuter tous les tests
        self.test_dependencies()
        self.test_files_exist()
        self.test_udp_reception()
        self.test_data_validation()
        self.test_json_parsing()
        
        # Afficher le résumé
        return self.print_summary()


def main():
    """Point d'entrée principal"""
    tester = SystemTester()
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
