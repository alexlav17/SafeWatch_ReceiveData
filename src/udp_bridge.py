"""Pont UDP -> SSE

Écoute sur UDP (par défaut 0.0.0.0:3333), décode les charges JSON et les transfère
dans le pipeline SSE temps réel + BD de l'application.
"""

import os
import json
import socket
import threading
from datetime import datetime

from src.api import realtime
from src.api.routes import _store_row

LISTEN_HOST = os.environ.get("UDP_BRIDGE_HOST", "0.0.0.0")
LISTEN_PORT = int(os.environ.get("UDP_BRIDGE_PORT", "3333"))
_BUFFER = 65535
_started = False


def _handle_packet(data, addr):
    txt = data.decode("utf-8", errors="ignore")
    print("Réception UDP de", addr, ":", txt)
    try:
        payload = json.loads(txt)
    except Exception as e:
        print("JSON invalide de", addr, ":", e)
        payload = {"raw": txt}

    id_ = payload.get("id") or f"{addr[0]}:{addr[1]}"
    type_ = payload.get("type") or ("ecg" if ("bpm" in payload or "ecg" in payload) else "raw")
    timestamp = payload.get("timestamp") or datetime.utcnow().isoformat() + "Z"

    # Extraire TOUS les champs numériques
    x = None
    y = None
    z = None
    bpm = None
    ir = None
    ecg = None
    
    try:
        # Accéléromètre
        x = float(payload.get("x")) if "x" in payload else 0.0
        y = float(payload.get("y")) if "y" in payload else 0.0
        z = float(payload.get("z")) if "z" in payload else 0.0
        
        # Capteur cardiaque
        if "bpm" in payload:
            bpm = float(payload.get("bpm"))
        if "ir" in payload:
            ir = int(payload.get("ir"))
        if "ecg" in payload:
            ecg = int(payload.get("ecg"))
    except Exception as e:
        print(f"Erreur extraction champs: {e}")
        x, y, z = 0.0, 0.0, 0.0

    raw = payload

    # Créer DEUX événements : un pour accel, un pour ecg
    # 1. Événement accéléromètre
    try:
        rowid_accel = _store_row(id_, "accel", timestamp, x or 0.0, y or 0.0, z or 0.0, raw,
                                  bpm=None, ir=None, ecg=None)
        event_accel = {
            "id": id_,
            "type": "accel",
            "timestamp": timestamp,
            "x": x or 0.0,
            "y": y or 0.0,
            "z": z or 0.0,
            "bpm": None,
            "ir": None,
            "ecg": None,
            "raw": raw,
            "rowid": rowid_accel
        }
        realtime.publish(event_accel)
        print(f"Événement accel publié: {event_accel}")
    except Exception as e:
        print("Erreur événement accel:", e)

    # 2. Événement ECG/cardiaque
    try:
        rowid_ecg = _store_row(id_, "ecg", timestamp, x or 0.0, y or 0.0, z or 0.0, raw,
                               bpm=bpm, ir=ir, ecg=ecg)
        event_ecg = {
            "id": id_,
            "type": "ecg",
            "timestamp": timestamp,
            "x": x or 0.0,
            "y": y or 0.0,
            "z": z or 0.0,
            "bpm": bpm,
            "ir": ir,
            "ecg": ecg,
            "raw": raw,
            "rowid": rowid_ecg
        }
        realtime.publish(event_ecg)
        print(f"Événement ecg publié: {event_ecg}")
    except Exception as e:
        print("Erreur événement ecg:", e)


def _listener(host=LISTEN_HOST, port=LISTEN_PORT):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    print(f"Pont UDP à l'écoute sur {host}:{port}")
    while True:
        data, addr = sock.recvfrom(_BUFFER)
        _handle_packet(data, addr)


def start_udp_bridge(host=LISTEN_HOST, port=LISTEN_PORT):
    global _started
    if _started:
        return
    t = threading.Thread(target=_listener, args=(host, port), daemon=True)
    t.start()
    _started = True
    return t


if __name__ == "__main__":
    start_udp_bridge()
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("UDP bridge stopped")
