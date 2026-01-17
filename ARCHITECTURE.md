# ESP32 Listener - Structure du Projet

## 📁 Application Principale (PRODUCTION)

### **flask_app.py** ⭐ APPLICATION FINALE
Interface web moderne avec WebSocket temps réel
- ❤️ Affichage BPM avec animation cœur battant
- 📊 Graphique ECG défilant (Chart.js, 30 secondes)
- 📐 Barres accéléromètre X/Y/Z
- 📝 Enregistrement CSV avec contrôles start/stop
- 🔌 UDP (port 3333) + WebSocket (Socket.IO)
- 📦 Buffer circulaire 60 secondes (600 échantillons)

**Démarrage:**
```bash
source venv/bin/activate
python flask_app.py
# OU
python start_server.py
```

**Interface:** http://192.168.206.212:5000

---

## 🧪 Applications de Test/Développement

### **src/main_sse_old.py** (ancien main.py)
Version SSE (Server-Sent Events) - architecture modulaire
- Utilise `src/udp_bridge.py`, `src/receive.py`, `src/ui.py`
- SSE au lieu de WebSocket
- Gardé pour référence/tests

### **start_server_old.py**
Ancien script de démarrage SSE - gardé pour référence

---

## 📊 Format des Données ESP32

**JSON attendu (port UDP 3333):**
```json
{
  "timestamp": "2026-01-14T15:30:00Z",
  "ecg": 2500,
  "bpm": 72,
  "x": 0.1,
  "y": -0.05,
  "z": 0.98
}
```

**Contraintes:**
- `ecg`: Valeur brute ADC (0-4095)
- `bpm`: Battements par minute (40-180 ou null)
- `x, y, z`: Accélération en g (±2.0)
- Fréquence: 10 Hz recommandé

---

## 🛠️ Outils de Test

### **simulate_esp32.py**
Simulateur pour tester sans ESP32 physique
```bash
python simulate_esp32.py --duration 30
```

### **test_udp.py, test_udp_simple.py**
Scripts de test UDP basiques

---

## 📦 Dépendances (requirements.txt)

```
Flask==3.0.0
Flask-SocketIO==5.3.5
eventlet==0.33.3
```

**Installation:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🔧 Configuration ESP32

Modifier [ESP32_EXEMPLE.ino](ESP32_EXEMPLE.ino):
```cpp
const char* ssid = "VotreSSID";
const char* password = "VotreMotDePasse";
const char* serverIP = "192.168.206.212";  // IP du Raspberry Pi
const int serverPort = 3333;
```
