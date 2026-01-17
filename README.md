# ESP32 Multi-Capteurs Listener 🚀

Serveur Python pour recevoir et visualiser en temps réel les données de **deux capteurs ESP32** :
- **BMA400** : Accéléromètre 3 axes
- **MAX86150** : Capteur cardiaque (BPM, IR, ECG)

Interface web temps réel avec graphiques interactifs, SSE (Server-Sent Events) et stockage SQLite.

---

## ✨ Fonctionnalités

- 📡 **Réception UDP** des données ESP32 (port 3333)
- 📊 **6 champs de données** : bpm, ir, ecg, x, y, z
- 📈 **Graphiques temps réel** : Accéléromètre 3D + ECG sélectionnable
- 💾 **Stockage SQLite** avec historique complet
- 🔴 **Server-Sent Events (SSE)** pour mise à jour instantanée
- 🎨 **Interface web responsive** avec Chart.js

---

## 📋 Prérequis

- **Raspberry Pi** (ou Linux/macOS/Windows)
- **Python 3.8+**
- **ESP32** avec BMA400 + MAX86150
- Réseau WiFi commun

---

## 🚀 Installation Rapide

### 1. Cloner le projet
```bash
git clone <repository-url>
cd esp32-listener
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Migrer la base de données
```bash
python3 migrate_db.py
```

### 4. Vérifier le système
```bash
python3 check_system.py
```
Doit afficher **Score: 5/5** ✅

### 5. Démarrer le serveur
```bash
python3 start_server.py
```

### 6. Ouvrir l'interface web
```
http://<IP-raspberry>:5000
```

---

## 📡 Configuration ESP32

Votre ESP32 doit envoyer un JSON UDP comme ceci :

```json
{
  "bpm": 72.5,
  "ir": 12450,
  "ecg": 8920,
  "x": 0.123,
  "y": -0.456,
  "z": 0.987
}
```

**Configuration réseau dans votre code C :**
```c
#define WIFI_SSID      "VotreSSID"
#define WIFI_PASS      "VotreMotDePasse"
#define RASPBERRY_IP   "192.168.1.17"  // IP du Raspberry Pi
#define UDP_PORT       3333
```

---

## 📁 Structure du projet

```
esp32-listener/
├── src/
│   ├── main.py              # Application Flask principale
│   ├── api/
│   │   ├── routes.py        # Endpoints API REST
│   │   └── realtime.py      # Gestionnaire SSE
│   ├── models/
│   │   └── sensor.py        # Modèle de données capteur
│   ├── services/
│   │   └── collector.py     # Collecteur de données
│   ├── config.py            # Configuration
│   ├── utils.py             # Utilitaires (validation, traitement)
│   ├── ui.py                # Interface HTML/JS
│   ├── receive.py           # Endpoint SSE
│   └── udp_bridge.py        # Bridge UDP → SSE
├── tests/
│   └── test_main.py         # Tests unitaires
├── migrate_db.py            # Migration base de données
├── check_system.py          # Vérification système
├── test_udp.py              # Test envoi UDP local
├── start_server.py          # Démarrage serveur complet
├── esp32_data.db            # Base SQLite (créée auto)
├── requirements.txt         # Dépendances Python
├── RECAP.md                 # Documentation complète
└── README.md                # Ce fichier
```

---

## 🚀 Utilisation

### Démarrage rapide
```bash
python3 start_server.py
```

Le serveur démarre sur `http://0.0.0.0:5000` et affiche :
- L'adresse web de l'interface
- L'IP/port pour la configuration ESP32
- Les informations de connexion

### Autres commandes utiles

```bash
# Vérifier le système
python3 check_system.py

# Tester localement (simule ESP32)
python3 test_udp.py

# Voir les dernières données
sqlite3 esp32_data.db "SELECT * FROM sensor_data ORDER BY rowid DESC LIMIT 10;"
```

---

## 📊 Interface Web

L'interface affiche en temps réel :

1. **Carte d'information** : Device ID, Type, Timestamp, valeurs actuelles
2. **Graphique Accéléromètre 3D** : Courbes X/Y/Z (200 points)
3. **Graphique Cardiaque** : BPM/IR/ECG sélectionnable (500 points)
4. **Tableaux historiques** : Accel + ECG

---

## 🔧 API REST

### POST `/api/sensor-data`
```json
{
  "id": "esp32-001",
  "type": "ecg",
  "bpm": 72.5,
  "ir": 12450,
  "ecg": 8920,
  "x": 0.123,
  "y": -0.456,
  "z": 0.987
}
```

### GET `/api/sensor-data/latest`
Dernière mesure

### GET `/events`
Stream SSE temps réel

---

## 🐛 Dépannage

### Les données n'apparaissent pas

1. **ESP32** : Vérifier les logs série (WiFi connecté + envoi UDP)
2. **Serveur** : Vérifier les logs Python (réception UDP)
3. **Navigateur** : Console F12 → "connected", "live"
4. **Test local** : `python3 test_udp.py`

### Erreur "Colonnes manquantes"
```bash
python3 migrate_db.py
```

---

## 📚 Documentation

- **[RECAP.md](RECAP.md)** : Guide complet
- **[MISE_A_JOUR.md](MISE_A_JOUR.md)** : Notes de mise à jour

---

## 🎉 Statut

✅ **Système opérationnel**
- ✅ 6 champs de données (bpm, ir, ecg, x, y, z)
- ✅ Interface web temps réel
- ✅ Bridge UDP actif
- ✅ Base de données migrée

**Score vérification : 5/5** ✨

---