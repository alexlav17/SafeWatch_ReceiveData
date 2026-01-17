import os
import json
from flask import Response
from src.ui import INDEX_HTML  # Import depuis src.ui

import sqlite3
from src.api import realtime
from src.api.routes import DB_FILENAME


def receive_data():
    """Générateur SSE: envoie un événement connecté + lignes récentes de la BD, puis transmet les événements temps réel.

    Cela garantit que l'interface reçoit un snapshot initial (historique) et un événement connecté
    avec le dernier id de ligne, que le frontend attend pour initialiser les graphiques/tableaux.
    """
    # Envoyer connecté avec le dernier rowid
    last_rowid = 0
    try:
        conn = sqlite3.connect(DB_FILENAME)
        cur = conn.cursor()
        cur.execute("SELECT MAX(rowid) FROM sensor_data;")
        r = cur.fetchone()
        conn.close()
        last_rowid = r[0] or 0
    except Exception:
        last_rowid = 0

    yield f"event: connected\ndata: {json.dumps({'last_rowid': last_rowid})}\n\n"

    # Envoyer l'historique récent (ordre ascendant)
    try:
        conn = sqlite3.connect(DB_FILENAME)
        cur = conn.cursor()
        cur.execute("SELECT rowid,id,type,timestamp,x,y,z,bpm,ir,ecg,raw FROM sensor_data ORDER BY rowid DESC LIMIT 200;")
        rows = cur.fetchall()
        conn.close()
        for row in reversed(rows):
            rowid, id_, type_, timestamp, x, y, z, bpm, ir, ecg, raw = row
            try:
                raw_json = json.loads(raw)
            except Exception:
                raw_json = raw
            payload = {
                'rowid': rowid, 'id': id_, 'type': type_, 'timestamp': timestamp,
                'x': x, 'y': y, 'z': z, 'bpm': bpm, 'ir': ir, 'ecg': ecg, 'raw': raw_json
            }
            yield f"event: measurement\ndata: {json.dumps(payload, default=str)}\n\n"
    except Exception:
        pass

    # Maintenant transmettre les événements en direct du flux en mémoire
    for ev in realtime.stream():
        yield ev