# 🚀 ESP32 Monitor - Visualisation Temps Réel

Solution complète pour visualiser les données ESP32 (capteur cardiaque + accéléromètre) en temps réel sur Raspberry Pi avec interface web moderne.

## 📋 Caractéristiques

### Interface Web
- ❤️ **Zone BPM** : Grand affichage numérique avec icône cœur animée
- 📈 **Graphique Signal** : Courbe défilante 30 secondes (300 points)
- 📊 **Accéléromètre** : 3 barres visuelles (X/Y/Z) avec valeurs numériques
- 🔌 **Statut** : Indicateur connexion + dernier paquet reçu
- 💾 **Contrôles CSV** : Start/Stop enregistrement avec indication visuelle

### Backend
- 📡 **Thread UDP** : Non-bloquant sur port 3333
- 🔄 **WebSocket** : Broadcasting vers tous les clients web via Socket.IO
- 💾 **Logging CSV** : Optionnel, activable depuis l'interface
- 🗄️ **Buffer circulaire** : 60 secondes d'historique (600 échantillons)

### Validation des données
- ⏱️ **Fréquence** : 10Hz (100ms entre paquets)
- 📊 **Signal cardiaque** : 200-3500 (ADC 12-bit)
- ❤️ **BPM valide** : 40-180 (sinon affiche "--")
- 📐 **Accélération** : ±2g (-2.0 à +2.0)

## 🔧 Installation

### Prérequis
- Raspberry Pi avec Python 3.7+
- Connexion réseau avec l'ESP32

### Installation des dépendances

```bash
# Naviguer vers le dossier du projet
cd /home/pi/Documents/esp32-listener

# Créer un environnement virtuel (recommandé)
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

## 🚀 Démarrage

### Option 1 : Interface Web Complète (Recommandé)

Lance le serveur Flask avec Socket.IO pour une interface web moderne :

```bash
python3 flask_app.py
```

L'interface sera accessible sur :
- **Local** : http://localhost:5000
- **Réseau** : http://[IP_RASPBERRY]:5000

Le serveur affichera l'IP exacte au démarrage.

### Option 2 : Récepteur Console (Mode Debug)

Pour tester la réception UDP sans interface web :

```bash
python3 raspberry_receiver_advanced.py
```

Options disponibles :
```bash
python3 raspberry_receiver_advanced.py --host 0.0.0.0 --port 3333
```

## 📡 Configuration ESP32

L'ESP32 doit envoyer des paquets UDP au format JSON sur le port **3333** :

### Format JSON attendu

```json
{
  "timestamp": "2026-01-14T10:30:45.123Z",
  "signal": 2450,
  "bpm": 72,
  "x": 0.145,
  "y": -0.023,
  "z": 0.987
}
```

### Champs
- `timestamp` : ISO 8601 (optionnel, généré si absent)
- `signal` : Valeur ADC du signal cardiaque (200-3500)
- `bpm` : Battements par minute (40-180, optionnel)
- `x`, `y`, `z` : Accélération en g (±2.0)

Alternative : Les champs `ecg` ou `ir` sont aussi acceptés comme signal.

### Configuration réseau ESP32

```cpp
// Dans votre code ESP32
const char* raspberryIP = "192.168.1.XXX";  // IP du Raspberry Pi
const uint16_t udpPort = 3333;

// Envoi UDP
WiFiUDP udp;
String json = "{\"signal\":" + String(signal) + 
              ",\"bpm\":" + String(bpm) + 
              ",\"x\":" + String(accelX) + 
              ",\"y\":" + String(accelY) + 
              ",\"z\":" + String(accelZ) + "}";
udp.beginPacket(raspberryIP, udpPort);
udp.print(json);
udp.endPacket();
```

## 📊 Utilisation de l'Interface Web

### Visualisation

1. **BPM** : Affichage grand format avec cœur animé
   - Valide : 40-180 BPM (vert)
   - Invalide : "--" (gris)

2. **Graphique Signal** : 
   - Défilement automatique
   - 30 secondes d'historique
   - Échelle 0-4000 (ADC 12-bit)

3. **Accéléromètre** :
   - Barres horizontales X (rouge), Y (vert), Z (bleu)
   - Point zéro au centre (0g)
   - Valeurs numériques à 3 décimales

### Enregistrement CSV

1. Cliquer sur **"▶️ Démarrer"** pour commencer l'enregistrement
2. Un fichier `data_esp32_YYYYMMDD_HHMMSS.csv` est créé
3. L'indicateur rouge clignote pendant l'enregistrement
4. Cliquer sur **"⏹️ Arrêter"** pour terminer

**Format CSV** :
```csv
timestamp,type,signal,bpm,accel_x,accel_y,accel_z
2026-01-14T10:30:45.123Z,sensor,2450,72,0.145,-0.023,0.987
```

### Contrôles

- **🗑️ Effacer** : Vide le graphique
- **Statut** : Affiche la connexion UDP et le dernier paquet

## 🔍 Dépannage

### Le serveur ne démarre pas

```bash
# Vérifier que le port 5000 est libre
sudo netstat -tulpn | grep 5000

# Ou utiliser un autre port
# Modifier dans flask_app.py : socketio.run(app, port=8080)
```

### Pas de données reçues

1. **Vérifier l'IP du Raspberry Pi** :
   ```bash
   hostname -I
   ```

2. **Vérifier le port UDP** :
   ```bash
   sudo netstat -ulpn | grep 3333
   ```

3. **Tester la réception UDP** :
   ```bash
   # Terminal 1 : Récepteur
   nc -ul 3333
   
   # Terminal 2 : Envoi test depuis un autre terminal
   echo '{"signal":2500,"bpm":75,"x":0.1,"y":0.2,"z":1.0}' | nc -u localhost 3333
   ```

### L'interface web ne se connecte pas

1. Vérifier que Flask-SocketIO est installé :
   ```bash
   pip list | grep Flask-SocketIO
   ```

2. Ouvrir la console du navigateur (F12) pour voir les erreurs

3. Vérifier le pare-feu :
   ```bash
   sudo ufw status
   sudo ufw allow 5000/tcp
   ```

### Problèmes de performances

Si l'interface lag avec 10Hz :

1. Réduire la durée du buffer dans `flask_app.py` :
   ```python
   BUFFER_DURATION = 30  # Au lieu de 60
   ```

2. Limiter les points affichés dans `templates/index.html` :
   ```javascript
   const maxSignalPoints = 150;  // Au lieu de 300
   ```

## 📁 Structure du Projet

```
esp32-listener/
├── flask_app.py                    # ⭐ Serveur principal Flask + Socket.IO
├── raspberry_receiver_advanced.py  # Récepteur console (debug)
├── requirements.txt                # Dépendances Python
├── templates/
│   └── index.html                  # ⭐ Interface web
├── data_esp32_*.csv                # Fichiers CSV générés
└── README_MONITOR.md               # Ce fichier
```

## 🎯 Fichiers Principaux

### `flask_app.py`
Serveur Flask avec :
- Thread UDP non-bloquant
- Broadcasting WebSocket
- Gestion buffer circulaire
- Enregistrement CSV

### `templates/index.html`
Interface web avec :
- Design responsive moderne
- Chart.js pour le graphique
- Socket.IO client
- Animations CSS

### `raspberry_receiver_advanced.py`
Récepteur console pour debug :
- Validation des données
- Affichage formaté
- Statistiques

## 📝 Exemples de Commandes

### Démarrage rapide
```bash
cd /home/pi/Documents/esp32-listener
python3 flask_app.py
```

### Avec environnement virtuel
```bash
cd /home/pi/Documents/esp32-listener
source venv/bin/activate
python3 flask_app.py
```

### Mode debug console
```bash
python3 raspberry_receiver_advanced.py
```

### Lancement au démarrage (systemd)

Créer `/etc/systemd/system/esp32-monitor.service` :

```ini
[Unit]
Description=ESP32 Monitor Web Interface
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Documents/esp32-listener
ExecStart=/home/pi/Documents/esp32-listener/venv/bin/python3 flask_app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Activer :
```bash
sudo systemctl enable esp32-monitor
sudo systemctl start esp32-monitor
sudo systemctl status esp32-monitor
```

## 📊 Monitoring et Logs

### Voir les logs en temps réel
```bash
# Si lancé manuellement
python3 flask_app.py

# Si lancé via systemd
sudo journalctl -u esp32-monitor -f
```

### Statistiques
Le serveur affiche toutes les 10 paquets :
```
📊 Paquets: 100 | BPM: 72 | Signal: 2450 | Accel: X=0.14 Y=-0.02 Z=0.99
```

## 🌐 Accès Distant

### Depuis un autre ordinateur sur le réseau

1. Trouver l'IP du Raspberry Pi :
   ```bash
   hostname -I
   # Exemple: 192.168.1.42
   ```

2. Ouvrir dans un navigateur :
   ```
   http://192.168.1.42:5000
   ```

### Depuis Internet (via port forwarding)

1. Configurer le routeur pour rediriger le port 5000 vers le Raspberry Pi
2. Utiliser l'IP publique ou un nom de domaine dynamique (DynDNS)

⚠️ **Attention** : Pas de sécurité par défaut, à utiliser uniquement sur réseau de confiance !

## 🔒 Sécurité (Production)

Pour un déploiement sécurisé :

1. **Ajouter une authentification** dans `flask_app.py`
2. **Utiliser HTTPS** avec un reverse proxy (nginx)
3. **Limiter les origines CORS**
4. **Utiliser un serveur WSGI** (gunicorn) au lieu de Werkzeug

## 📞 Support

Pour des problèmes :
1. Vérifier les logs du serveur
2. Vérifier la console du navigateur (F12)
3. Tester avec `raspberry_receiver_advanced.py` d'abord
4. Vérifier la configuration réseau ESP32

## 📄 Licence

Ce projet est fourni tel quel pour usage éducatif et personnel.

---

**Créé le 14 janvier 2026** - ESP32 Realtime Monitor v1.0
