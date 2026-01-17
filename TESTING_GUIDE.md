# 🧪 GUIDE DE TEST - ESP32 Monitor

Guide complet pour tester le système sans ESP32 réel.

## 🎯 Test Rapide (Sans ESP32)

### Option 1 : Test Automatique (Recommandé)

**Terminal 1** - Lancer le serveur :
```bash
cd /home/pi/Documents/esp32-listener
python3 flask_app.py
```

**Terminal 2** - Lancer le simulateur :
```bash
python3 simulate_esp32.py
```

**Navigateur** - Ouvrir l'interface :
```
http://localhost:5000
```

Vous devriez voir les données défiler en temps réel ! 🎉

### Option 2 : Test Manuel UDP

**Terminal 1** - Lancer le serveur :
```bash
python3 flask_app.py
```

**Terminal 2** - Envoyer un paquet test :
```bash
echo '{"signal":2500,"bpm":75,"x":0.1,"y":0.2,"z":1.0}' | nc -u localhost 3333
```

**Navigateur** - Vérifier l'interface :
```
http://localhost:5000
```

Le paquet devrait apparaître instantanément !

## 🔬 Tests Avancés

### Test 1 : Validation des Plages de Valeurs

**Tester BPM invalide (doit afficher "--")** :
```bash
# BPM trop bas (< 40)
echo '{"signal":2500,"bpm":20,"x":0,"y":0,"z":1}' | nc -u localhost 3333

# BPM trop haut (> 180)
echo '{"signal":2500,"bpm":200,"x":0,"y":0,"z":1}' | nc -u localhost 3333
```

**Tester BPM valide (40-180)** :
```bash
echo '{"signal":2500,"bpm":72,"x":0,"y":0,"z":1}' | nc -u localhost 3333
```

### Test 2 : Validation Signal Cardiaque

**Signal dans la plage (200-3500)** :
```bash
echo '{"signal":2500,"bpm":72,"x":0,"y":0,"z":1}' | nc -u localhost 3333
```

**Signal hors plage (sera clampé)** :
```bash
# Trop bas (sera mis à 200)
echo '{"signal":50,"bpm":72,"x":0,"y":0,"z":1}' | nc -u localhost 3333

# Trop haut (sera mis à 3500)
echo '{"signal":5000,"bpm":72,"x":0,"y":0,"z":1}' | nc -u localhost 3333
```

### Test 3 : Validation Accéléromètre

**Accélération dans la plage (±2g)** :
```bash
echo '{"signal":2500,"bpm":72,"x":1.5,"y":-0.8,"z":0.3}' | nc -u localhost 3333
```

**Accélération hors plage (sera clampée)** :
```bash
# Hors plage (sera limité à ±2g)
echo '{"signal":2500,"bpm":72,"x":5.0,"y":-3.0,"z":10.0}' | nc -u localhost 3333
```

### Test 4 : Fréquence 10Hz

**Envoyer 100 paquets à 10Hz** :
```bash
python3 simulate_esp32.py --frequency 10 --duration 10
```

Vérifier dans l'interface que :
- Le graphique défile sans à-coups
- Le compteur augmente régulièrement
- Aucun paquet n'est perdu

### Test 5 : Enregistrement CSV

1. Ouvrir l'interface : `http://localhost:5000`
2. Lancer le simulateur : `python3 simulate_esp32.py --duration 30`
3. Cliquer sur "▶️ Démarrer" dans l'interface
4. Attendre 30 secondes
5. Cliquer sur "⏹️ Arrêter"
6. Vérifier le fichier CSV :

```bash
ls -lh data_esp32_*.csv
head -20 data_esp32_*.csv
```

Format attendu :
```csv
timestamp,type,signal,bpm,accel_x,accel_y,accel_z
2026-01-14T10:30:45.123Z,sensor,2500,72,0.145,-0.023,0.987
```

### Test 6 : Multi-Clients WebSocket

**Ouvrir 3 onglets du navigateur** :
```
http://localhost:5000
http://localhost:5000
http://localhost:5000
```

**Lancer le simulateur** :
```bash
python3 simulate_esp32.py
```

**Vérifier** : Les 3 onglets doivent tous recevoir les mêmes données simultanément.

### Test 7 : Résilience

**Test de déconnexion/reconnexion** :

1. Lancer le serveur et ouvrir l'interface
2. Arrêter le serveur (Ctrl+C)
3. Vérifier que l'interface affiche "Déconnecté" 🔴
4. Relancer le serveur
5. Vérifier que l'interface se reconnecte automatiquement 🟢

### Test 8 : Buffer Circulaire

**Vérifier que le buffer est limité à 600 échantillons (60s)** :

1. Lancer le serveur et le simulateur
2. Attendre 2 minutes
3. Vérifier dans les logs du serveur que le buffer ne dépasse pas 600 éléments

### Test 9 : Performance

**Test de charge** :
```bash
# Simuler 50 Hz au lieu de 10 Hz
python3 simulate_esp32.py --frequency 50 --duration 60
```

**Vérifier** :
- CPU du Raspberry Pi (ne doit pas dépasser 50%)
- Latence de l'interface (doit rester < 100ms)
- Pas de perte de paquets

## 📊 Checklist de Test Complète

### ✅ Tests Fonctionnels

- [ ] Serveur démarre sans erreur
- [ ] Interface web accessible
- [ ] WebSocket se connecte
- [ ] Réception UDP fonctionne
- [ ] Données s'affichent en temps réel
- [ ] BPM valide (40-180) affiché
- [ ] BPM invalide affiche "--"
- [ ] Signal cardiaque dans plage (200-3500)
- [ ] Accéléromètre dans plage (±2g)
- [ ] Graphique défile correctement
- [ ] Barres d'accéléromètre bougent
- [ ] Compteur de paquets augmente
- [ ] Dernier paquet mis à jour

### ✅ Tests CSV

- [ ] Bouton "Démarrer" active l'enregistrement
- [ ] Indicateur rouge "Recording" affiché
- [ ] Nom de fichier affiché
- [ ] Bouton "Arrêter" désactive l'enregistrement
- [ ] Fichier CSV créé
- [ ] Format CSV correct
- [ ] Données valides dans CSV

### ✅ Tests Réseau

- [ ] Multi-clients supporté
- [ ] Reconnexion automatique
- [ ] Pas de perte de paquets à 10Hz
- [ ] Latence acceptable (< 100ms)

### ✅ Tests Interface

- [ ] Design responsive (mobile/desktop)
- [ ] Animations fluides
- [ ] Pas d'erreurs JavaScript (F12)
- [ ] Boutons fonctionnels
- [ ] Statuts correctement affichés

## 🐛 Débogage

### Activer le mode verbeux

**Dans flask_app.py**, ajouter en haut :
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Dans l'interface web**, ouvrir la console (F12) :
```javascript
// Afficher tous les événements Socket.IO
socket.onAny((event, ...args) => {
  console.log('Socket event:', event, args);
});
```

### Surveiller le trafic UDP

**Terminal 1** - Capturer les paquets :
```bash
sudo tcpdump -i any -n port 3333 -A
```

**Terminal 2** - Envoyer un paquet :
```bash
echo '{"signal":2500,"bpm":72,"x":0,"y":0,"z":1}' | nc -u localhost 3333
```

### Vérifier les ports ouverts

```bash
sudo netstat -tulpn | grep -E ':(5000|3333)'
```

Doit afficher :
```
udp    0.0.0.0:3333    0.0.0.0:*    python3
tcp    0.0.0.0:5000    0.0.0.0:*    python3
```

## 📈 Métriques de Performance

### Utilisation CPU

```bash
top -p $(pgrep -f flask_app.py)
```

**Attendu** : < 20% CPU à 10Hz

### Utilisation Mémoire

```bash
ps aux | grep flask_app.py
```

**Attendu** : < 100 MB RAM

### Taux de paquets

```bash
# Dans les logs du serveur, toutes les 10 secondes
# Doit afficher ~100 paquets
```

## 🎓 Scénarios de Test Complets

### Scénario 1 : Démarrage à Froid

```bash
# 1. Tout arrêter
pkill -f flask_app
pkill -f simulate_esp32

# 2. Lancer le serveur
python3 flask_app.py &

# 3. Attendre 2 secondes
sleep 2

# 4. Ouvrir l'interface
xdg-open http://localhost:5000

# 5. Lancer le simulateur
python3 simulate_esp32.py --duration 60

# 6. Vérifier que tout fonctionne
```

### Scénario 2 : Marche/Arrêt ESP32

```bash
# Simuler des déconnexions/reconnexions ESP32
for i in {1..5}; do
  echo "Cycle $i/5"
  python3 simulate_esp32.py --duration 10
  sleep 5
done
```

L'interface doit continuer à fonctionner sans planter.

### Scénario 3 : Session Longue Durée

```bash
# Test 1 heure
python3 simulate_esp32.py --duration 3600
```

Vérifier :
- Pas de fuite mémoire
- Buffer reste stable à 600 éléments
- Interface reste responsive

## ✅ Validation Finale

Si tous ces tests passent :

✨ **Votre système est prêt pour l'ESP32 réel !** ✨

Il suffit de :
1. Configurer l'IP du Raspberry dans l'ESP32
2. Téléverser le code ESP32
3. Profiter du monitoring en temps réel !

---

**Tests réussis ?** → Passez à [QUICK_START.md](QUICK_START.md) pour le déploiement final.
