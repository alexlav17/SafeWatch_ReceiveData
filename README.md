# ESP32 Listener — Guide en français

Ce projet fournit un petit serveur Python pour recevoir des données (ex. accéléromètre) envoyées par un ESP32 (C3). Le service expose une API REST pour l'ingestion et le stockage des mesures.

## Structure du projet

```
esp32-listener
├── src
│   ├── main.py                # Crée l'application Flask (ne démarre pas le serveur directement)
│   ├── api
│   │   ├── __init__.py        # Marque le répertoire api comme un package
│   │   └── routes.py          # Définit les routes de l'API pour la réception des données
│   ├── services
│   │   └── collector.py        # Contient la classe Collector pour le traitement des données
│   ├── models
│   │   └── sensor.py          # Définit la classe Sensor pour les lectures des capteurs
│   ├── config.py              # Paramètres de configuration pour l'application
│   └── utils.py               # Fonctions utilitaires pour le traitement et la validation des données
├── tests
│   └── test_main.py           # Tests unitaires pour la logique principale de l'application
├── requirements.txt           # Liste des dépendances du projet
├── .env                       # Variables d'environnement pour la configuration
├── .gitignore                 # Fichiers à ignorer par Git
├── Dockerfile                 # Instructions pour la création d'une image Docker
└── README.md                  # Documentation du projet
```

## Prérequis

- Python 3.8+ (sur Raspberry Pi / Linux)
- pip

## Installation

1. Cloner le dépôt :
   ```
   git clone <repository-url>
   cd esp32-listener
   ```

2. Installer les dépendances requises :
   ```
   pip install -r requirements.txt
   ```

## Configuration

- Éditez `src/config.py` ou créez un fichier `.env` si vous préférez charger des variables d'environnement.
- Paramètres utiles : `host`, `port`, `sensor_data_endpoint`.

## Lancer le serveur (réception des données)

- Depuis le répertoire racine du projet :
  ```
  python3 receivemain.py
  ```
  Le serveur écoute sur l'adresse et le port définis dans `src/config.py` (par défaut `0.0.0.0:5000`).

## Usage

Une fois le serveur en cours d'exécution, vous pouvez envoyer des requêtes aux routes API définies pour acquérir des données depuis l'ESP32 C3. Reportez-vous au fichier `src/api/routes.py` pour les points de terminaison disponibles et leur utilisation.

## Envoyer des données (test local)

- Utilisez `sendmain.py` pour simuler un ESP32 :
  ```
  python3 sendmain.py
  ```
  Ce script envoie périodiquement des JSON au point de terminaison configuré.

### Exemple d'envoi depuis un ESP32 (Arduino/PlatformIO)

- Utiliser HTTP POST vers : `http://<IP_RPI>:5000/api/sensor-data`
- Payload JSON attendu : `{ "id": "...", "type": "accelerometer", "x": <float>, "y": <float>, "z": <float> }`

## Notes

- Les données reçues sont validées via `src/utils.py` et stockées dans une base SQLite (`esp32_data.db`) ou selon la logique définie dans `src/api/routes.py`.
- `main.py` n'exécute pas le serveur directement afin de faciliter les tests et l'importation depuis d'autres scripts ; utilisez `receivemain.py` pour démarrer en local.
- Pour la production, utilisez un serveur WSGI (gunicorn/uwsgi) derrière un reverse proxy.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.