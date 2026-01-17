from flask import Blueprint, request, jsonify, Response
import os
import json
import sqlite3
import sys
from datetime import datetime

# Assurer que le package src est dans le chemin pour les imports
if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.utils import validate_sensor_data, process_sensor_data
from src.api import realtime  # publier les événements aux clients SSE

api_bp = Blueprint('api', __name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB_FILENAME = os.path.join(PROJECT_ROOT, 'esp32_data.db')

def init_db():
    conn = sqlite3.connect(DB_FILENAME)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sensor_data (
        id TEXT,
        type TEXT,
        timestamp TEXT,
        x REAL,
        y REAL,
        z REAL,
        bpm REAL,
        ir INTEGER,
        ecg INTEGER,
        raw TEXT
    );
    """)
    conn.commit()
    conn.close()

init_db()

def _store_row(id_, type_, timestamp, x, y, z, raw, bpm=None, ir=None, ecg=None):
    conn = sqlite3.connect(DB_FILENAME)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO sensor_data (id, type, timestamp, x, y, z, bpm, ir, ecg, raw)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (id_, type_, timestamp, x, y, z, bpm, ir, ecg, json.dumps(raw)))
    lastrowid = cur.lastrowid
    conn.commit()
    conn.close()
    return lastrowid

@api_bp.route('/sensor-data', methods=['POST'])
def receive_sensor_data():
    # Lecture flexible de la charge utile
    data = request.get_json(silent=True)
    if data is None:
        if request.form:
            try:
                data = request.form.to_dict()
            except Exception:
                data = None
        else:
            raw = request.get_data(as_text=True)
            try:
                data = json.loads(raw) if raw else None
            except Exception:
                data = None

    # Log reçu pour débogage
    client = request.remote_addr
    print(f"[{datetime.utcnow().isoformat()}] Requête POST de {client} -> endpoint {request.path}")
    print("Données brutes:", request.get_data(as_text=True))
    print("JSON analysé:", data)

    if data is None:
        return jsonify({'status': 'error', 'message': 'Pas de charge JSON ou corps illisible'}), 400

    # Validation simple
    try:
        validate_sensor_data(data)
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

    processed = process_sensor_data(data)
    timestamp = data.get('timestamp') or datetime.utcnow().isoformat() + 'Z'

    try:
        bpm = processed.get('bpm')
        ir = processed.get('ir')
        ecg = processed.get('ecg')
        _store_row(processed['id'], processed['type'], timestamp,
                   processed['x'], processed['y'], processed['z'], data,
                   bpm=bpm, ir=ir, ecg=ecg)
    except Exception as e:
        print("Error storing to DB:", e)
        return jsonify({'status': 'error', 'message': 'DB error'}), 500

    # Publier aux clients SSE (temps réel)
    try:
        event_payload = {
            "id": processed['id'],
            "type": processed['type'],
            "timestamp": timestamp,
            "x": processed['x'],
            "y": processed['y'],
            "z": processed['z'],
            "bpm": processed.get('bpm'),
            "ir": processed.get('ir'),
            "ecg": processed.get('ecg'),
            "raw": data
        }
        realtime.publish(event_payload)
    except Exception as e:
        print("Erreur lors de la publication de l'événement temps réel:", e)

    # Retourner le contenu traité pour vérification du client
    return jsonify({'status': 'received', 'timestamp': timestamp, 'data': processed}), 200

@api_bp.route('/sensor-data/latest', methods=['GET'])
def latest():
    try:
        conn = sqlite3.connect(DB_FILENAME)
        cur = conn.cursor()
        cur.execute("SELECT id,type,timestamp,x,y,z,bpm,ir,ecg,raw FROM sensor_data ORDER BY rowid DESC LIMIT 1;")
        row = cur.fetchone()
        conn.close()
        if not row:
            return jsonify({'status':'empty'}), 200
        id_, type_, timestamp, x, y, z, bpm, ir, ecg, raw = row
        return jsonify({
            'status': 'ok',
            'data': {
                'id': id_,
                'type': type_,
                'timestamp': timestamp,
                'x': x, 'y': y, 'z': z,
                'bpm': bpm, 'ir': ir, 'ecg': ecg,
                'raw': json.loads(raw)
            }
        }), 200
    except Exception as e:
        return jsonify({'status':'error','message': str(e)}), 500

@api_bp.route('/stream', methods=['GET'])
def stream_events():
    """
    Endpoint SSE. Les clients se connectent à /stream pour recevoir les mesures en temps réel.
    """
    return Response(realtime.stream(), mimetype='text/event-stream')