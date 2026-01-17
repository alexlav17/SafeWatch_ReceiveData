# 🔄 NOUVEAU FORMAT - ECG + BPM UNIQUEMENT

## ⚠️ Changements Importants

**L'IR n'existe plus !** Le système utilise maintenant uniquement :
- **ECG** : Signal cardiaque brut (valeur ADC)
- **BPM** : Battements par minute (40-180)
- **Accéléromètre** : X, Y, Z (±2g)

---

## 📡 Nouveau Format JSON

### Format Complet
```json
{
  "ecg": 2450,
  "bpm": 72,
  "x": 0.145,
  "y": -0.023,
  "z": 0.987,
  "timestamp": "2026-01-14T10:30:45.123Z"
}
```

### Format Minimal (avec valeurs par défaut)
```json
{
  "ecg": 2450,
  "bpm": 72
}
```

**Champs obligatoires :**
- `ecg` : Signal ECG (nombre entier, valeur ADC brute)
- Ou au minimum un champ numérique

**Champs optionnels :**
- `bpm` : Battements/minute (validé 40-180, sinon affiche "--")
- `x`, `y`, `z` : Accéléromètre (défaut: 0.0 si absent)
- `timestamp` : ISO 8601 (généré automatiquement si absent)

---

## 🔧 Code ESP32 Mis à Jour

### Code Minimal

```cpp
#include <WiFi.h>
#include <WiFiUdp.h>

const char* ssid = "VOTRE_WIFI";
const char* password = "VOTRE_PASSWORD";
const char* raspberryIP = "192.168.1.42";  // ← CHANGER
const uint16_t udpPort = 3333;

WiFiUDP udp;
const int ECG_PIN = 34;  // Pin ADC pour ECG

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) delay(500);
  
  analogReadResolution(12);  // 12-bit ADC
  pinMode(ECG_PIN, INPUT);
  
  Serial.println("✅ Connecté au WiFi");
  Serial.printf("📡 Envoi vers %s:%d\n", raspberryIP, udpPort);
}

void loop() {
  // Lire l'ECG
  int ecg = analogRead(ECG_PIN);
  
  // TODO: Calculer le BPM
  int bpm = 72;  // Valeur fixe pour test
  
  // Créer le JSON
  String json = "{\"ecg\":" + String(ecg) + 
                ",\"bpm\":" + String(bpm) + "}";
  
  // Envoyer via UDP
  udp.beginPacket(raspberryIP, udpPort);
  udp.print(json);
  udp.endPacket();
  
  Serial.println(json);
  delay(100);  // 10Hz
}
```

---

## 🧪 Test Rapide

### Option 1 : Script Automatique

```bash
./test_new_format.sh
```

Ce script envoie 5 paquets de test avec différents cas.

### Option 2 : Test Manuel

```bash
# Paquet complet
echo '{"ecg":2450,"bpm":72,"x":0.1,"y":0.2,"z":1.0}' | nc -u localhost 3333

# Paquet minimal
echo '{"ecg":2500,"bpm":75}' | nc -u localhost 3333

# Paquet sans BPM
echo '{"ecg":2600}' | nc -u localhost 3333
```

### Option 3 : Simulateur

```bash
# Terminal 1 - Serveur
python3 flask_app.py

# Terminal 2 - Simulateur (déjà adapté)
python3 simulate_esp32.py
```

---

## 📊 Validation Automatique

### BPM
- ✅ **Plage valide** : 40 - 180
- ❌ **Hors plage** : Affiche "--" dans l'interface
- ℹ️ **Absent** : Affiche "--" dans l'interface

### ECG
- ✅ **Toute valeur** : Acceptée (pas de validation de plage)
- ℹ️ **Absent** : Le paquet est ignoré

### Accéléromètre
- ✅ **Plage valide** : -2.0 à +2.0 g
- ⚠️ **Hors plage** : Clampé automatiquement à ±2.0
- ℹ️ **Absent** : Défaut à 0.0

---

## 🔍 Dépannage

### ❌ "Pas de données reçues"

**1. Vérifier que le serveur tourne :**
```bash
python3 flask_app.py
```

Vous devriez voir :
```
📡 Thread UDP démarré sur 0.0.0.0:3333
```

**2. Tester avec un paquet manuel :**
```bash
echo '{"ecg":2500,"bpm":72}' | nc -u localhost 3333
```

Vous devriez voir dans les logs :
```
✅ Paquet reçu de ('127.0.0.1', XXXXX): {"ecg":2500,"bpm":72}
   ECG: 2500
   BPM: 72.0
📤 Données envoyées via WebSocket
📊 Paquet #1 | BPM: 72 | ECG: 2500 | Accel: X=0.00 Y=0.00 Z=0.00
```

**3. Vérifier l'interface web :**
- Ouvrir `http://localhost:5000`
- Vérifier l'indicateur "Connecté" (vert)
- Le compteur de paquets doit augmenter
- Les valeurs ECG et BPM doivent s'afficher

### ❌ "BPM affiche toujours --"

Vérifiez que le BPM est dans la plage 40-180 :
```bash
# BPM valide (72)
echo '{"ecg":2500,"bpm":72}' | nc -u localhost 3333

# BPM invalide (trop haut, affichera --)
echo '{"ecg":2500,"bpm":200}' | nc -u localhost 3333
```

### ❌ "ECG ne s'affiche pas"

Assurez-vous que le champ `ecg` est présent :
```bash
# Correct
echo '{"ecg":2500}' | nc -u localhost 3333

# Incorrect (ancien format avec 'signal')
echo '{"signal":2500}' | nc -u localhost 3333  # ❌ Ne fonctionnera plus
```

### ❌ "Erreur JSON"

Vérifiez la syntaxe JSON :
```bash
# Correct
echo '{"ecg":2500,"bpm":72}' | nc -u localhost 3333

# Incorrect (guillemets manquants)
echo '{ecg:2500,bpm:72}' | nc -u localhost 3333  # ❌
```

---

## 📝 CSV Généré

Le nouveau format CSV est :
```csv
timestamp,ecg,bpm,accel_x,accel_y,accel_z
2026-01-14T10:30:45.123Z,2450,72,0.145,-0.023,0.987
2026-01-14T10:30:45.223Z,2480,73,0.150,-0.020,0.990
```

Plus de colonne `type` ou `signal`, juste `ecg` et `bpm`.

---

## ✅ Checklist de Migration

- [ ] Code ESP32 mis à jour pour utiliser `ecg` au lieu de `signal`
- [ ] Code ESP32 n'envoie plus de champ `ir`
- [ ] Serveur `flask_app.py` redémarré
- [ ] Interface web rafraîchie (Ctrl+F5)
- [ ] Test manuel réussi (`./test_new_format.sh`)
- [ ] ESP32 configuré avec la bonne IP
- [ ] Données reçues et affichées dans l'interface

---

## 🎯 Format Attendu

**ANCIEN (ne fonctionne plus) :**
```json
{
  "signal": 2450,    // ❌ Remplacé par "ecg"
  "ir": 1234,        // ❌ Supprimé
  "bpm": 72
}
```

**NOUVEAU (correct) :**
```json
{
  "ecg": 2450,       // ✅ Signal ECG brut
  "bpm": 72,         // ✅ Battements/minute
  "x": 0.1,          // ✅ Optionnel
  "y": 0.2,          // ✅ Optionnel
  "z": 1.0           // ✅ Optionnel
}
```

---

## 🚀 Commandes Essentielles

```bash
# Démarrer le serveur
python3 flask_app.py

# Tester la réception
python3 raspberry_receiver_advanced.py

# Test automatique
./test_new_format.sh

# Simulateur
python3 simulate_esp32.py

# Interface web
firefox http://localhost:5000
```

---

**✅ Le système est maintenant adapté au nouveau capteur ECG !**

Tous les fichiers ont été mis à jour :
- ✅ `flask_app.py` - Backend adapté
- ✅ `templates/index.html` - Interface adaptée
- ✅ `simulate_esp32.py` - Simulateur adapté
- ✅ `ESP32_EXEMPLE.ino` - Code ESP32 adapté
- ✅ `raspberry_receiver_advanced.py` - Receiver adapté

**Le logging est maintenant très verbeux pour vous aider à déboguer !**
