# Projet par Alexandre Lavallée SLIMANI Ryan MOUJANE Choukry

## Présentation

Ce projet est un **serveur de réception et de visualisation en temps réel** pour des données envoyées par un **ESP32**.

Le serveur :
- écoute des **paquets UDP** (port **3333**) contenant du **JSON**,
- diffuse les mesures en **temps réel** vers une page Web (WebSocket / Socket.IO),
- affiche un **ECG**, un **BPM** et l’**accéléromètre** (x/y/z),
- peut enregistrer des fichiers CSV et des logs d’anomalies (fichiers générés à l’exécution).

## Démarrage rapide

### 1) Pré-requis

- Python 3
- pip

### 2) Installer

```bash
cd /home/pi/Documents/esp32-listener
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3) Lancer le serveur

Méthode recommandée :

```bash
python3 start_server.py
```

Ou directement :

```bash
python3 flask_app.py
```

### 4) Ouvrir l’interface

Dans un navigateur :

```
http://<IP_DU_RASPBERRY>:5000
```

Trouver l’IP :

```bash
hostname -I
```

## Format des données attendues (ESP32 → UDP 3333)

Le format recommandé est :

```json
{
  "timestamp": "2026-01-14T10:30:45.123Z",
  "ecg": 2450,
  "bpm": 72,
  "x": 0.145,
  "y": -0.023,
  "z": 0.987
}
```

Notes :
- `ecg` est la valeur brute (ADC) du signal ECG.
- `bpm` est validé (plage typique 40–180). Si absent ou invalide, l’UI affichera `--`.
- `x`, `y`, `z` sont l’accélération (souvent en g). Si absent, le serveur met 0.0.
- `timestamp` est optionnel (généré automatiquement si absent).

### Champs optionnels pour anomalies

Le serveur peut aussi recevoir des champs de classification d’anomalies envoyés par l’ESP32, par exemple :

```json
{
  "anomaly_type": "FALL_CRITICAL",
  "anomaly_severity": "CRITICAL",
  "bpm": 50,
  "bpm_valid": true,
  "signal_valid": true,
  "alert": true
}
```

## Comment ça marche (simple)

1) Un thread UDP écoute `0.0.0.0:3333`.
2) Chaque paquet JSON est parsé et normalisé (ECG/BPM/accel/timestamp).
3) Les données sont diffusées à tous les navigateurs connectés via Socket.IO.
4) Optionnel : écriture dans des fichiers CSV (session) et un log d’anomalies.

## Structure (fichiers principaux)

- `flask_app.py` : application principale (UDP + Socket.IO + UI)
- `start_server.py` : lance l’application principale
- `templates/index.html` : page Web (UI)
- `simulate_esp32.py` : simulateur d’envoi de données
- `test_udp.py` / `test_udp_simple.py` : tests UDP basiques
- `ESP32_EXEMPLE.ino` : exemple de sketch ESP32

## Tester sans ESP32

1) Lancer le serveur
2) Dans un autre terminal :

```bash
python3 simulate_esp32.py
```

## Dépannage rapide

- Pas de page Web : vérifier le port 5000 et l’IP.
- Pas de données : vérifier que l’ESP32 envoie bien en UDP sur le port 3333.
- Port déjà utilisé : arrêter le processus qui écoute sur 5000.

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
