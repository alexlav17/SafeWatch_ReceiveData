from flask import Blueprint, request, jsonify, Response
import os
import json
import sqlite3
from datetime import datetime

from src.utils import validate_sensor_data, process_sensor_data
from src.api import realtime  # publish events to SSE clients

api_bp = Blueprint('api', __name__, url_prefix='/api')

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
        raw TEXT
    );
    """)
    conn.commit()
    conn.close()

init_db()

def _store_row(id_, type_, timestamp, x, y, z, raw):
    conn = sqlite3.connect(DB_FILENAME)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO sensor_data (id, type, timestamp, x, y, z, raw)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (id_, type_, timestamp, x, y, z, json.dumps(raw)))
    conn.commit()
    conn.close()

@api_bp.route('/sensor-data', methods=['POST'])
def receive_sensor_data():
    # lecture flexible du payload
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

    # log reçu pour debug
    client = request.remote_addr
    print(f"[{datetime.utcnow().isoformat()}] Requete POST de {client} -> endpoint {request.path}")
    print("Raw data:", request.get_data(as_text=True))
    print("Parsed JSON:", data)

    if data is None:
        return jsonify({'status': 'error', 'message': 'No JSON payload or unreadable body'}), 400

    # validation simple
    try:
        validate_sensor_data(data)
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

    processed = process_sensor_data(data)
    timestamp = data.get('timestamp') or datetime.utcnow().isoformat() + 'Z'

    try:
        _store_row(processed['id'], processed['type'], timestamp,
                   processed['x'], processed['y'], processed['z'], data)
    except Exception as e:
        print("Error storing to DB:", e)
        return jsonify({'status': 'error', 'message': 'DB error'}), 500

    # publish to SSE clients (real-time)
    try:
        event_payload = {
            "id": processed['id'],
            "type": processed['type'],
            "timestamp": timestamp,
            "x": processed['x'],
            "y": processed['y'],
            "z": processed['z'],
            "raw": data
        }
        realtime.publish(event_payload)
    except Exception as e:
        print("Error publishing realtime event:", e)

    # retourne le contenu traité pour vérification client
    return jsonify({'status': 'received', 'timestamp': timestamp, 'data': processed}), 200

@api_bp.route('/sensor-data/latest', methods=['GET'])
def latest():
    try:
        conn = sqlite3.connect(DB_FILENAME)
        cur = conn.cursor()
        cur.execute("SELECT id,type,timestamp,x,y,z,raw FROM sensor_data ORDER BY rowid DESC LIMIT 1;")
        row = cur.fetchone()
        conn.close()
        if not row:
            return jsonify({'status':'empty'}), 200
        id_, type_, timestamp, x, y, z, raw = row
        return jsonify({
            'status': 'ok',
            'data': {
                'id': id_,
                'type': type_,
                'timestamp': timestamp,
                'x': x, 'y': y, 'z': z,
                'raw': json.loads(raw)
            }
        }), 200
    except Exception as e:
        return jsonify({'status':'error','message': str(e)}), 500

@api_bp.route('/stream', methods=['GET'])
def stream_events():
    """
    SSE endpoint. Clients connect to /api/stream to receive real-time measurements.
    """
    return Response(realtime.stream(), mimetype='text/event-stream')