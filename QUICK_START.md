# 🚀 DÉMARRAGE RAPIDE - ESP32 Monitor

Guide ultra-rapide pour lancer votre système de monitoring ESP32 en 5 minutes.

## ⚡ Installation Express (3 minutes)

### 1. Installer les dépendances

```bash
cd /home/pi/Documents/esp32-listener
pip3 install -r requirements.txt
```

### 2. Lancer le serveur

**Méthode automatique** (recommandé):
```bash
./quick_start.sh
```

**Méthode manuelle**:
```bash
python3 flask_app.py
```

### 3. Ouvrir l'interface web

Le serveur affiche l'URL au démarrage :
```
http://[IP_DU_RASPBERRY]:5000
```

Exemple : `http://192.168.1.42:5000`

## 📡 Configuration ESP32 (2 minutes)

### 1. Ouvrir le fichier exemple

Fichier fourni : [ESP32_EXEMPLE.ino](ESP32_EXEMPLE.ino)

### 2. Modifier 3 lignes

```cpp
const char* ssid = "VOTRE_WIFI";           // Ligne 15
const char* password = "VOTRE_PASSWORD";    // Ligne 16
const char* raspberryIP = "192.168.1.42";  // Ligne 19 ← IP DU RASPBERRY
```

### 3. Téléverser sur l'ESP32

Via Arduino IDE ou PlatformIO.

## ✅ Test de Fonctionnement

### Terminal du Raspberry Pi doit afficher :

```
📊 Paquets: 10 | BPM: 72 | Signal: 2450 | Accel: X=0.14 Y=-0.02 Z=0.99
📊 Paquets: 20 | BPM: 75 | Signal: 2480 | Accel: X=0.15 Y=-0.03 Z=0.98
```

### Interface Web doit montrer :

- ❤️ BPM qui change en temps réel
- 📈 Graphique qui défile
- 📊 Barres d'accéléromètre qui bougent
- 🟢 Indicateur "Connecté"

## 🔧 Commandes Utiles

### Trouver l'IP du Raspberry Pi
```bash
hostname -I
```

### Tester la réception UDP
```bash
python3 raspberry_receiver_advanced.py
```

### Arrêter le serveur
Appuyer sur `Ctrl + C` dans le terminal

### Redémarrer le serveur
```bash
python3 flask_app.py
```

## 🆘 Problèmes Courants

### ❌ "Port already in use"
```bash
# Tuer le processus sur le port 5000
sudo lsof -ti:5000 | xargs sudo kill -9
```

### ❌ "Module not found"
```bash
# Réinstaller les dépendances
pip3 install --upgrade -r requirements.txt
```

### ❌ Pas de données reçues

1. **Vérifier l'IP dans l'ESP32**
   ```bash
   hostname -I  # Sur le Raspberry
   ```

2. **Vérifier le WiFi de l'ESP32**
   - Ouvrir le moniteur série (115200 baud)
   - Doit afficher "✅ WiFi connecté!"

3. **Tester UDP manuellement**
   ```bash
   # Terminal 1 (Raspberry)
   nc -ul 3333
   
   # Terminal 2 (même machine, test local)
   echo '{"signal":2500,"bpm":75,"x":0.1,"y":0.2,"z":1.0}' | nc -u localhost 3333
   ```

### ❌ Interface web blanche

1. Ouvrir la console du navigateur (F12)
2. Vérifier les erreurs JavaScript
3. Vérifier que `templates/index.html` existe

## 📊 Format des Données Attendu

L'ESP32 doit envoyer du JSON UDP sur le port 3333 :

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

**Contraintes** :
- `signal` : 200-3500
- `bpm` : 40-180 (optionnel)
- `x`, `y`, `z` : -2.0 à +2.0

## 🎯 Checklist Complète

- [ ] Python 3 installé sur Raspberry Pi
- [ ] Dépendances installées (`pip3 install -r requirements.txt`)
- [ ] Serveur lancé (`python3 flask_app.py`)
- [ ] IP du Raspberry Pi connue (`hostname -I`)
- [ ] ESP32 connecté au WiFi
- [ ] IP du Raspberry configurée dans l'ESP32
- [ ] Code ESP32 téléversé
- [ ] Interface web accessible dans le navigateur
- [ ] Données reçues (compteur de paquets augmente)

## 🎉 C'est Tout !

Si tous les voyants sont au vert :
- Le BPM s'affiche ❤️
- Le graphique défile 📈
- Les barres bougent 📊

**→ Votre système fonctionne !**

## 📚 Documentation Complète

Pour plus de détails : [README_MONITOR.md](README_MONITOR.md)

---

**Problème non résolu ?** Vérifiez les logs du serveur et le moniteur série de l'ESP32.
