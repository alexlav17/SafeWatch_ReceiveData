# 🔄 Mise à jour Multi-Capteurs (BMA400 + MAX86150)

## ✅ Modifications appliquées

Votre système a été mis à jour pour recevoir et afficher **TOUTES** les données des deux capteurs :

### 📊 Données reçues

#### Capteur Cardiaque (MAX86150)
- **BPM** : Battements par minute (fréquence cardiaque)
- **IR** : Signal infrarouge brut
- **ECG** : Signal ECG brut

#### Accéléromètre (BMA400)
- **X, Y, Z** : Accélération en G sur les 3 axes

---

## 🛠️ Fichiers modifiés

### 1. Base de données (`src/api/routes.py`)
- ✅ Ajout des colonnes `bpm`, `ir`, `ecg` à la table `sensor_data`
- ✅ Mise à jour de `_store_row()` pour stocker tous les champs
- ✅ Mise à jour de l'endpoint `/sensor-data/latest` pour retourner tous les champs

### 2. Réception UDP (`src/udp_bridge.py`)
- ✅ Extraction correcte de **tous les champs** du JSON ESP32
- ✅ Publication SSE avec bpm, ir, ecg, x, y, z

### 3. Stream SSE (`src/receive.py`)
- ✅ Envoi de tous les champs aux clients web

### 4. Interface Web (`src/ui.py`)
- ✅ Affichage des valeurs BPM, IR, ECG dans le tableau
- ✅ Graphique temps réel avec sélection BPM/IR/ECG
- ✅ Synchronisation correcte des 3 datasets du graphique cardiaque

### 5. Utilitaires (`src/utils.py`)
- ✅ `process_sensor_data()` extrait maintenant bpm, ir, ecg
- ✅ Validation plus souple (accepte les paquets partiels)

---

## 🚀 Démarrage

### 1. Migrer la base de données existante
```bash
python3 migrate_db.py
```

### 2. Tester la réception UDP
```bash
# Dans un terminal
python3 test_udp.py
```

### 3. Lancer le serveur
```bash
python3 src/main.py
# Ou si vous utilisez un autre script de démarrage
```

### 4. Ouvrir l'interface
Ouvrir `http://<ip-raspberry>:5000` dans votre navigateur

---

## 📡 Format des données ESP32

Votre ESP32 envoie maintenant ce JSON via UDP :
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

**Tous les champs sont maintenant correctement reçus et affichés !**

---

## 🎯 Ce qui s'affiche sur le site

### En temps réel :
- **Carte principale** : BPM actuel (si type=ecg) OU X/Y/Z (si type=accelerometer)
- **Graphique accéléromètre** : Courbes X, Y, Z en temps réel
- **Graphique ECG** : Sélection entre BPM / IR / ECG avec échelles adaptées
- **Tableau historique** : Dernières mesures accélérométriques
- **Tableau ECG** : Dernières mesures cardiaques avec BPM, IR, ECG

### Vérifications :
1. ✅ Les données BPM s'affichent dans la carte et le graphique
2. ✅ Les valeurs IR et ECG sont visibles dans le tableau
3. ✅ L'accéléromètre (x, y, z) continue de fonctionner
4. ✅ Le graphique permet de basculer entre BPM/IR/ECG
5. ✅ Tous les champs sont stockés dans la base de données

---

## 🔍 Déboggage

### Vérifier la réception UDP
```bash
# Les logs doivent afficher :
Réception UDP de ('192.168.1.xxx', 12345) : {"bpm":72.5,"ir":12450,"ecg":8920,"x":0.123,"y":-0.456,"z":0.987}
Événement publié: {'id': '192.168.1.xxx:12345', 'type': 'ecg', 'bpm': 72.5, 'ir': 12450, 'ecg': 8920, 'x': 0.123, 'y': -0.456, 'z': 0.987}
```

### Vérifier la base de données
```bash
sqlite3 esp32_data.db "SELECT id, bpm, ir, ecg, x, y, z FROM sensor_data ORDER BY rowid DESC LIMIT 5;"
```

### Tester avec des données simulées
```bash
python3 test_udp.py
# Cela envoie un paquet complet avec tous les champs
```

---

## ⚠️ Notes importantes

1. **Migration DB** : Si vous aviez déjà des données, lancez `migrate_db.py` pour ajouter les colonnes manquantes
2. **Type auto** : Le bridge UDP détecte automatiquement le type "ecg" si bpm/ir/ecg sont présents
3. **Compatibilité** : L'ancien format (x=bpm) continue de fonctionner en fallback
4. **NULL values** : Les champs peuvent être NULL si le capteur ne les envoie pas

---

## ✨ Résultat final

🎉 **Votre système reçoit et affiche maintenant :**
- ✅ **6 champs** de données (au lieu de 3)
- ✅ **2 capteurs** distincts (BMA400 + MAX86150)
- ✅ **3 graphiques** temps réel (Accel 3D + ECG sélectionnable)
- ✅ **2 tableaux** historiques (Accel + ECG)
- ✅ **100% des données** stockées en base
