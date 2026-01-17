#!/usr/bin/env python3
"""
Vérification complète du système multi-capteurs
"""
import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(__file__))

def check_database():
    """Vérifier la structure de la base de données"""
    import sqlite3
    from src.api.routes import DB_FILENAME
    
    print("=== VÉRIFICATION BASE DE DONNÉES ===")
    
    if not os.path.exists(DB_FILENAME):
        print("❌ Base de données introuvable")
        print(f"   Chemin attendu: {DB_FILENAME}")
        return False
    
    conn = sqlite3.connect(DB_FILENAME)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(sensor_data)")
    columns = [col[1] for col in cur.fetchall()]
    conn.close()
    
    print(f"✅ Base trouvée: {DB_FILENAME}")
    print(f"   Colonnes: {', '.join(columns)}")
    
    required = ['x', 'y', 'z', 'bpm', 'ir', 'ecg']
    missing = [col for col in required if col not in columns]
    
    if missing:
        print(f"⚠️  Colonnes manquantes: {', '.join(missing)}")
        print("   → Exécutez: python3 migrate_db.py")
        return False
    
    print("✅ Toutes les colonnes requises sont présentes")
    return True

def check_imports():
    """Vérifier que tous les modules sont importables"""
    print("\n=== VÉRIFICATION IMPORTS ===")
    
    modules = [
        ('src.api.routes', 'Routes API'),
        ('src.api.realtime', 'SSE temps réel'),
        ('src.udp_bridge', 'Bridge UDP'),
        ('src.receive', 'Receive SSE'),
        ('src.utils', 'Utilitaires'),
    ]
    
    all_ok = True
    for module, name in modules:
        try:
            __import__(module)
            print(f"✅ {name}: OK")
        except Exception as e:
            print(f"❌ {name}: {e}")
            all_ok = False
    
    return all_ok

def test_process_data():
    """Tester le traitement des données"""
    print("\n=== TEST TRAITEMENT DONNÉES ===")
    
    from src.utils import process_sensor_data
    
    # Test 1: Données complètes (tous les capteurs)
    test_data = {
        "id": "esp32-test",
        "type": "ecg",
        "bpm": 75.5,
        "ir": 15000,
        "ecg": 9500,
        "x": 0.1,
        "y": -0.2,
        "z": 0.98
    }
    
    try:
        result = process_sensor_data(test_data)
        
        if all(k in result for k in ['bpm', 'ir', 'ecg', 'x', 'y', 'z']):
            print("✅ Données complètes traitées correctement")
            print(f"   → {result}")
        else:
            print("⚠️  Champs manquants dans le résultat")
            print(f"   → {result}")
            return False
    except Exception as e:
        print(f"❌ Erreur traitement: {e}")
        return False
    
    # Test 2: Données partielles (accel seulement)
    test_data_accel = {
        "id": "esp32-test",
        "type": "accelerometer",
        "x": 0.05,
        "y": -0.1,
        "z": 1.0
    }
    
    try:
        result = process_sensor_data(test_data_accel)
        print("✅ Données accéléromètre seul: OK")
        print(f"   → {result}")
    except Exception as e:
        print(f"❌ Erreur accel: {e}")
        return False
    
    return True

def check_udp_config():
    """Vérifier la configuration UDP"""
    print("\n=== CONFIGURATION UDP ===")
    
    from src.udp_bridge import LISTEN_HOST, LISTEN_PORT
    
    print(f"✅ Écoute configurée sur {LISTEN_HOST}:{LISTEN_PORT}")
    print(f"   → Votre ESP32 doit envoyer vers cette IP:PORT")
    
    return True

def check_esp32_config():
    """Afficher un récapitulatif de la config ESP32"""
    print("\n=== CONFIGURATION ESP32 ATTENDUE ===")
    
    print("""
Votre ESP32 doit envoyer un JSON UDP comme ceci:
{
  "bpm": 72.5,      // Battements par minute
  "ir": 12450,      // Signal infrarouge
  "ecg": 8920,      // Signal ECG
  "x": 0.123,       // Accel X
  "y": -0.456,      // Accel Y
  "z": 0.987        // Accel Z
}

Sur le port 3333 vers l'IP du Raspberry Pi.
    """)
    
    return True

def main():
    print("╔═══════════════════════════════════════════╗")
    print("║  VÉRIFICATION SYSTÈME MULTI-CAPTEURS      ║")
    print("╚═══════════════════════════════════════════╝\n")
    
    checks = [
        ("Base de données", check_database),
        ("Imports Python", check_imports),
        ("Traitement données", test_process_data),
        ("Configuration UDP", check_udp_config),
        ("Config ESP32", check_esp32_config),
    ]
    
    results = []
    for name, func in checks:
        try:
            results.append(func())
        except Exception as e:
            print(f"❌ Erreur dans {name}: {e}")
            results.append(False)
    
    print("\n" + "="*50)
    print("RÉSUMÉ")
    print("="*50)
    
    total = len(results)
    passed = sum(results)
    
    for i, (name, _) in enumerate(checks):
        status = "✅" if results[i] else "❌"
        print(f"{status} {name}")
    
    print("\n" + f"Score: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 SYSTÈME PRÊT ! Vous pouvez:")
        print("   1. Lancer le serveur: python3 src/main.py")
        print("   2. Flasher votre ESP32 avec le code C fourni")
        print("   3. Ouvrir http://<IP-raspberry>:5000 dans votre navigateur")
        print("   4. Tester avec: python3 test_udp.py")
    else:
        print("\n⚠️  Actions requises:")
        if not results[0]:
            print("   → python3 migrate_db.py")
        if not results[1]:
            print("   → Vérifier les dépendances Python")

if __name__ == '__main__':
    main()
