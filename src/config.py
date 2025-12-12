import os

# bind du serveur (dans le conteneur laisser 0.0.0.0)
host = os.getenv("FLASK_BIND_HOST", "0.0.0.0")
port = int(os.getenv("FLASK_PORT", 5000))
debug = os.getenv("FLASK_DEBUG", "True").lower() in ("1", "true", "yes")
database_url = "sqlite:///esp32_data.db"
sensor_data_endpoint = "/api/sensor-data"

# adresse que les clients utiliseront pour se connecter.
# Par défaut : IP LAN du Raspberry (utilisé par ESP32 / autres appareils du réseau).
# Pour tests locaux dans le conteneur/host, tu peux remplacer par "127.0.0.1".
server_host = os.getenv("ESP32_SERVER_HOST", "192.168.64.212")