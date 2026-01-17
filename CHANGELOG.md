# Changelog - Système Multi-Capteurs ESP32

## Version 2.0.0 - Support Multi-Capteurs (13 janvier 2026)

### 🎯 Objectif
Étendre le système pour recevoir et afficher les données de **deux capteurs** ESP32 simultanément :
- BMA400 (accéléromètre)
- MAX86150 (capteur cardiaque)

### ✨ Nouvelles fonctionnalités

#### 1. Support de 6 champs de données
- ✅ **bpm** (float) : Battements par minute
- ✅ **ir** (int) : Signal infrarouge brut
- ✅ **ecg** (int) : Signal ECG brut
- ✅ **x** (float) : Accélération axe X
- ✅ **y** (float) : Accélération axe Y
- ✅ **z** (float) : Accélération axe Z

#### 2. Base de données étendue
- Ajout des colonnes `bpm`, `ir`, `ecg` à la table `sensor_data`
- Script de migration automatique (`migrate_db.py`)
- Rétrocompatibilité avec les anciennes données

#### 3. Interface web améliorée
- Graphique ECG avec sélection BPM/IR/ECG
- Tableau séparé pour les données cardiaques
- Échelles adaptatives selon le type de donnée
- Synchronisation parfaite des datasets

#### 4. Outils de développement
- `check_system.py` : Vérification complète du système
- `test_udp.py` : Test d'envoi UDP simulé
- `start_server.py` : Démarrage unifié du serveur

### 🔧 Modifications techniques

#### Fichiers modifiés

##### `src/api/routes.py`
```python
# Avant
CREATE TABLE sensor_data (x, y, z, ...)

# Après
CREATE TABLE sensor_data (x, y, z, bpm, ir, ecg, ...)

# Fonction _store_row étendue
def _store_row(..., bpm=None, ir=None, ecg=None)
```

##### `src/udp_bridge.py`
```python
# Avant : extraction uniquement x, y, z (ou bpm dans x)

# Après : extraction de tous les champs
x = float(payload.get("x")) if "x" in payload else 0.0
bpm = float(payload.get("bpm")) if "bpm" in payload else None
ir = int(payload.get("ir")) if "ir" in payload else None
ecg = int(payload.get("ecg")) if "ecg" in payload else None
```

##### `src/receive.py`
```python
# Avant
SELECT rowid,id,type,timestamp,x,y,z,raw FROM sensor_data

# Après
SELECT rowid,id,type,timestamp,x,y,z,bpm,ir,ecg,raw FROM sensor_data
```

##### `src/utils.py`
```python
# Avant : validation stricte (x, y, z obligatoires)

# Après : validation souple (accepte les paquets partiels)
def process_sensor_data(data):
    processed = {
        "x": float(data.get('x', 0.0)),
        "y": float(data.get('y', 0.0)),
        "z": float(data.get('z', 0.0)),
    }
    
    # Ajouter les champs cardiaques si présents
    if 'bpm' in data:
        processed['bpm'] = float(data['bpm'])
    if 'ir' in data:
        processed['ir'] = int(data['ir'])
    if 'ecg' in data:
        processed['ecg'] = int(data['ecg'])
    
    return processed
```

##### `src/ui.py`
```python
// Avant : affichage bpm dans le champ x

// Après : extraction séparée de tous les champs
const bpm = (m.bpm !== undefined && m.bpm !== null) ? m.bpm : ...
const ir = (m.ir !== undefined && m.ir !== null) ? m.ir : ...
const ecg = (m.ecg !== undefined && m.ecg !== null) ? m.ecg : ...

// Synchronisation des 3 datasets du graphique ECG
ecgChart.data.datasets[0].data.push(bpmValue);  // BPM
ecgChart.data.datasets[1].data.push(irValue);   // IR
ecgChart.data.datasets[2].data.push(ecgValue);  // ECG
```

#### Nouveaux fichiers

- **`migrate_db.py`** : Migration base de données (ajoute bpm, ir, ecg)
- **`check_system.py`** : Vérification système complète (5 tests)
- **`test_udp.py`** : Simulateur de paquets UDP ESP32
- **`start_server.py`** : Démarrage unifié (Flask + UDP bridge)
- **`RECAP.md`** : Documentation complète utilisateur
- **`MISE_A_JOUR.md`** : Notes de mise à jour détaillées
- **`START_HERE.txt`** : Guide de démarrage rapide
- **`CHANGELOG.md`** : Ce fichier

### 🧪 Tests

#### Score de vérification
```bash
$ python3 check_system.py

Score: 5/5 ✅
```

#### Tests effectués
1. ✅ Structure de la base de données
2. ✅ Imports Python
3. ✅ Traitement des données (paquets complets et partiels)
4. ✅ Configuration UDP
5. ✅ Compatibilité ESP32

### 📊 Métriques

- **Champs de données** : 3 → 6 (+100%)
- **Capteurs supportés** : 1 → 2 (+100%)
- **Graphiques temps réel** : 1 → 2 (+100%)
- **Tableaux historiques** : 1 → 2 (+100%)
- **Taux de couverture** : 100% des champs ESP32

### 🔄 Migration

#### Avant (v1.0)
```json
{
  "id": "esp32-001",
  "type": "accelerometer",
  "x": 0.123,
  "y": -0.456,
  "z": 0.987
}
```

#### Après (v2.0)
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

### ⚠️ Breaking Changes

#### Base de données
- Les anciennes bases **doivent** être migrées avec `migrate_db.py`
- Rétrocompatibilité : les anciennes données conservent `NULL` pour bpm/ir/ecg

#### API
- Aucun breaking change
- Les anciens clients (x, y, z only) continuent de fonctionner
- Les nouveaux champs sont optionnels

### 🚀 Déploiement

```bash
# 1. Migrer la base de données
python3 migrate_db.py

# 2. Vérifier le système
python3 check_system.py

# 3. Démarrer le serveur
python3 start_server.py
```

### 📝 Notes

- **Compatibilité ascendante** : Les anciens paquets (x, y, z only) fonctionnent toujours
- **Détection automatique** : Le type "ecg" est automatiquement détecté si bpm/ir/ecg sont présents
- **Performances** : Aucun impact sur les performances (même nombre de requêtes)
- **Stockage** : +3 colonnes SQLite (impact négligeable)

### 🐛 Bugs corrigés

1. ✅ Import `ui` → `src.ui` dans receive.py
2. ✅ Validation trop stricte dans utils.py (accepte maintenant les paquets partiels)
3. ✅ Synchronisation des datasets du graphique ECG
4. ✅ Affichage incorrect de bpm (était dans x)

### 🔮 Futures améliorations possibles

- [ ] Support d'autres capteurs (température, humidité, etc.)
- [ ] Filtrage des données en temps réel
- [ ] Export CSV/JSON des données
- [ ] Alertes sur seuils (BPM trop élevé, etc.)
- [ ] Authentification utilisateur
- [ ] Support multi-ESP32 (plusieurs devices)

---

## Version 1.0.0 - Version initiale

### Fonctionnalités
- Réception HTTP POST des données accéléromètre
- Stockage SQLite
- Interface web basique
- SSE temps réel
