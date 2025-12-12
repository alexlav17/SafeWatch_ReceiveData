import os
import json
from flask import Response
from ui import INDEX_HTML  # Assurez-vous que ce fichier existe

# DB path (ajustez si nécessaire)
DB_PATH = os.path.join(os.path.dirname(__file__), "esp32_data.db")

def receive_data():
    """Fonction pour recevoir des données et les envoyer au client."""
    # Logique pour recevoir des données
    # Exemple : récupérer des données de la base de données
    last_rowid = get_max_rowid()  # Exemple d'appel à une fonction pour obtenir le max rowid
    yield f"event: connected\ndata: {json.dumps({'last_rowid': last_rowid})}\n\n"
    
    # Logique pour continuer à recevoir des données
    while True:
        # Exemple de récupération de nouvelles données
        new_data = fetch_new_data()  # Implémentez cette fonction selon vos besoins
        yield f"data: {json.dumps(new_data)}\n\n"

def get_max_rowid():
    # Implémentez la logique pour obtenir le max rowid
    pass

def fetch_new_data():
    # Implémentez la logique pour récupérer de nouvelles données
    pass