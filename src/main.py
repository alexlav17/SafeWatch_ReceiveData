from flask import Flask, Response, render_template_string
from config import host, port, debug
from receive import receive_data  # Importation de la fonction pour recevoir des données
from ui import INDEX_HTML  # Importation du HTML

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/events')
def events():
    return Response(receive_data(), content_type='text/event-stream')

if __name__ == "__main__":
    print(f"Starting Flask on {host}:{port}")
    app.run(host=host, port=port, debug=debug, threaded=True)