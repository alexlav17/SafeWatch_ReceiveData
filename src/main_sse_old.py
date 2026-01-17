import os
import sys
# Assurer que la racine du projet (parent de src/) est sur sys.path afin que `import src.*` fonctionne
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, Response, render_template_string
from config import host, port, debug
from receive import receive_data  # Importation de la fonction pour recevoir des données
from ui import INDEX_HTML  # Importation du HTML
from src.api.routes import api_bp  # Importation du blueprint API

app = Flask(__name__)
app.register_blueprint(api_bp)  # Enregistrer le blueprint API

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/events')
def events():
    # Utiliser le mimetype (préféré) et désactiver la mise en cache du buffering/proxy
    return Response(receive_data(), mimetype='text/event-stream', headers={'Cache-Control':'no-cache', 'X-Accel-Buffering':'no'})

if __name__ == "__main__":
    # Quand le reloader de debug Flask est activé, Werkzeug lance un processus enfant séparé
    # pour exécuter l'app. On doit démarrer le pont UDP uniquement dans le
    # *processus enfant du reloader* (le vrai processus serveur) afin qu'il partage la même
    # mémoire avec la file d'attente SSE `realtime` en mémoire.
    is_server_process = os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not debug
    if is_server_process:
        try:
            from src.udp_bridge import start_udp_bridge
            start_udp_bridge()
            print("Pont UDP démarré dans le processus serveur")
        except Exception as e:
            print("Avertissement: échec du démarrage du pont UDP:", e)
    else:
        print("Pas de démarrage du pont UDP dans le processus parent (reloader)")

    print(f"Starting Flask on {host}:{port}")
    app.run(host=host, port=port, debug=debug, threaded=True)