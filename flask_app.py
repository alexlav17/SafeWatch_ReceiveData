#!/usr/bin/env python3
"""
Serveur Flask avec Socket.IO pour visualisation temps réel des données ESP32
- Thread UDP non-bloquant (port 3333)
- Broadcasting WebSocket vers tous les clients web
- Buffer circulaire 60 secondes
- Logging CSV optionnel
"""

import eventlet
eventlet.monkey_patch()

import os
import sys
import json
import socket
import threading
import csv
from datetime import datetime
from collections import deque
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

# Configuration
UDP_PORT = 3333
UDP_HOST = '0.0.0.0'
SAMPLE_RATE = 10  # Hz

# États globaux
app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'esp32-realtime-monitor'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Buffer ILLIMITÉ pour stocker tout l'historique (pas de maxlen!)
signal_buffer = deque()  # Stockage illimité
accel_buffer = deque()   # Stockage illimité
session_start_time = None  # Heure de début de session

# État CSV
csv_logging = False
csv_file = None
csv_writer = None
csv_lock = threading.Lock()

# Statistiques
stats = {
    'packets_received': 0,
    'last_packet_time': None,
    'udp_running': False
}

# État anomalies
anomalies_file = 'anomalies_log.csv'
anomalies_lock = threading.Lock()
anomaly_active = False
anomaly_start_time = None
anomaly_data = []

# Seuils de détection d'anomalies
ANOMALY_BPM_MIN = 40
ANOMALY_BPM_MAX = 150
ANOMALY_ACCEL_THRESHOLD = 1.5  # Accélération >1.5g considérée comme anormale
ANOMALY_MIN_DURATION = 2  # Secondes minimum pour confirmer une anomalie


def init_anomalies_log():
    """Initialise le fichier CSV des anomalies"""
    if not os.path.exists(anomalies_file):
        with open(anomalies_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'start_time', 'end_time', 'duration_seconds', 
                'anomaly_type', 'bpm_min', 'bpm_max', 'bpm_avg',
                'accel_x_max', 'accel_y_max', 'accel_z_max',
                'severity', 'description'
            ])


def calculate_bpm(raw_value, prev_values):
    """
    Calcule le BPM à partir du signal cardiaque brut
    Utilise une détection de pics simple
    """
    # Pour une implémentation basique, on peut retourner une valeur mockée
    # ou implémenter un vrai algorithme de détection de pics
    # Ici, on suppose que l'ESP32 envoie déjà le BPM calculé
    return None


def validate_bpm(bpm):
    """Valide que le BPM est dans la plage acceptable (40-180)"""
    if bpm is None:
        return None
    try:
        bpm_val = float(bpm)
        if 40 <= bpm_val <= 180:
            return bpm_val
        return None
    except (ValueError, TypeError):
        return None


def start_csv_logging():
    """Démarre l'enregistrement CSV"""
    global csv_logging, csv_file, csv_writer
    
    with csv_lock:
        if csv_logging:
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'data_esp32_{timestamp}.csv'
        
        csv_file = open(filename, 'w', newline='')
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([
            'timestamp', 'ecg', 'bpm', 
            'accel_x', 'accel_y', 'accel_z'
        ])
        csv_logging = True
        
        print(f"📝 Enregistrement CSV démarré: {filename}")
        return filename


def stop_csv_logging():
    """Arrête l'enregistrement CSV"""
    global csv_logging, csv_file, csv_writer
    
    with csv_lock:
        if not csv_logging:
            return
        
        csv_logging = False
        if csv_file:
            csv_file.close()
            csv_file = None
            csv_writer = None
        
        print("⏹️  Enregistrement CSV arrêté")


def log_to_csv(data):
    """Enregistre une ligne dans le CSV si activé"""
    global csv_writer
    
    with csv_lock:
        if csv_logging and csv_writer:
            try:
                csv_writer.writerow([
                    data.get('timestamp', datetime.now().isoformat()),
                    data.get('ecg', ''),
                    data.get('bpm', ''),
                    data.get('accel_x', ''),
                    data.get('accel_y', ''),
                    data.get('accel_z', '')
                ])
                csv_file.flush()
            except Exception as e:
                print(f"❌ Erreur CSV: {e}")


def classifier_anomalie(packet_data):
    """
    Classification des anomalies basée sur les données ESP32
    L'ESP32 envoie déjà le type et la sévérité détectés
    
    Format attendu:
    {
        "anomaly_type": "FALL_CRITICAL" | "CONVULSION" | "FALL_DETECTED" | ...
        "anomaly_severity": "CRITICAL" | "MODERATE" | "NONE"
        "bpm": float,
        "signal_valid": bool,
        "bpm_valid": bool,
        "alert": bool
    }
    
    Retourne: (type_fr, severity_fr, niveau_urgence, action, delai)
    """
    anomaly_type = packet_data.get('anomaly_type', 'NONE')
    anomaly_severity = packet_data.get('anomaly_severity', 'NONE')
    bpm = packet_data.get('bpm')
    bpm_valid = packet_data.get('bpm_valid', False)
    signal_valid = packet_data.get('signal_valid', False)
    
    # Mapping types ESP32 -> Français
    type_mapping = {
        'FALL_CRITICAL': 'chute_critique',
        'CONVULSION': 'convulsion',
        'FALL_DETECTED': 'chute_détectée',
        'DIFFICULTY_STANDING': 'difficulté_relever',
        'BPM_CRITICAL_LOW': 'bradycardie_critique',
        'BPM_CRITICAL_HIGH': 'tachycardie_critique',
        'BPM_LOW': 'bradycardie_légère',
        'NONE': 'aucune'
    }
    
    type_fr = type_mapping.get(anomaly_type, anomaly_type.lower())
    
    # === CLASSIFICATION SELON SÉVÉRITÉ ESP32 ===
    
    # ANOMALIES CRITIQUES - Intervention immédiate
    if anomaly_severity == "CRITICAL":
        
        if anomaly_type == "FALL_CRITICAL":
            return (
                type_fr,
                'critique',
                'URGENCE_MAXIMALE',
                'Chute avec immobilité - Personne possiblement inconsciente',
                0  # Intervention immédiate
            )
        
        elif anomaly_type == "CONVULSION":
            return (
                type_fr,
                'critique',
                'URGENCE_MEDICALE',
                'Convulsion détectée après chute',
                0  # Intervention immédiate
            )
        
        elif anomaly_type == "FALL_DETECTED":
            return (
                type_fr,
                'critique',
                'SURVEILLANCE_ACTIVE',
                'Chute détectée - Analyse en cours (5s)',
                5  # Attendre analyse
            )
        
        elif anomaly_type == "BPM_CRITICAL_LOW":
            bpm_str = f"{bpm:.0f}" if bpm else "?"
            return (
                type_fr,
                'critique',
                'ALERTE_MEDICALE',
                f'Bradycardie sévère: {bpm_str} bpm (< 35)',
                10
            )
        
        elif anomaly_type == "BPM_CRITICAL_HIGH":
            bpm_str = f"{bpm:.0f}" if bpm else "?"
            return (
                type_fr,
                'critique',
                'ALERTE_MEDICALE',
                f'Tachycardie sévère: {bpm_str} bpm (> 150)',
                10
            )
        
        else:
            # Type critique inconnu
            return (
                type_fr,
                'critique',
                'ALERTE_CRITIQUE',
                f'Anomalie critique: {anomaly_type}',
                0
            )
    
    # ANOMALIES MODÉRÉES - Surveillance renforcée
    elif anomaly_severity == "MODERATE":
        
        if anomaly_type == "DIFFICULTY_STANDING":
            return (
                type_fr,
                'grave',  # On garde 'grave' pour l'affichage (orange)
                'ASSISTANCE_SUGGEREE',
                'Difficulté à se relever - Chutes multiples',
                30
            )
        
        elif anomaly_type == "BPM_LOW":
            bpm_str = f"{bpm:.0f}" if bpm else "?"
            return (
                type_fr,
                'modéré',
                'INFORMATION',
                f'BPM légèrement bas: {bpm_str} bpm (< 50)',
                None
            )
        
        else:
            return (
                type_fr,
                'modéré',
                'SURVEILLANCE',
                f'Anomalie modérée: {anomaly_type}',
                None
            )
    
    # Pas d'anomalie
    else:
        return (
            'aucune',
            'normal',
            'MONITORING',
            'Données normales',
            None
        )


def format_anomaly_log(type_fr, severity_fr, niveau_urgence, message, delai):
    """
    Formate le log d'anomalie pour affichage
    """
    emoji_map = {
        'critique': '🚨',
        'grave': '⛔',
        'modéré': '⚠️',
        'normal': '✅'
    }
    
    emoji = emoji_map.get(severity_fr, '❓')
    delai_str = f"{delai}s" if delai is not None else "aucun"
    
    return f"{emoji} {severity_fr.upper()} | {niveau_urgence} | {message} | Délai: {delai_str}"


def save_anomaly(start_time, end_time, anomaly_data_buffer):
    """
    Sauvegarde une anomalie dans le fichier CSV et les données brutes en JSON
    """
    with anomalies_lock:
        try:
            duration = (end_time - start_time).total_seconds()
            
            # Calculer les statistiques
            bpms = [d['bpm'] for d in anomaly_data_buffer if d.get('bpm') is not None]
            bpm_min = min(bpms) if bpms else None
            bpm_max = max(bpms) if bpms else None
            bpm_avg = sum(bpms) / len(bpms) if bpms else None
            
            accel_x_max = max([abs(d['accel_x']) for d in anomaly_data_buffer])
            accel_y_max = max([abs(d['accel_y']) for d in anomaly_data_buffer])
            accel_z_max = max([abs(d['accel_z']) for d in anomaly_data_buffer])
            
            # Déterminer le type d'anomalie (déjà analysé lors de la détection)
            anomaly_type = anomaly_data_buffer[0].get('anomaly_type', 'inconnue')
            severity = anomaly_data_buffer[0].get('severity', 'modéré')
            
            print(f"   💾 Sauvegarde anomalie: {anomaly_type} | Sévérité: {severity.upper()}")
            
            # Créer un ID unique pour l'anomalie
            anomaly_id = start_time.strftime('%Y%m%d_%H%M%S')
            
            # Sauvegarder les données brutes en JSON pour visualisation
            json_dir = 'anomalies_data'
            if not os.path.exists(json_dir):
                os.makedirs(json_dir)
            
            json_file = os.path.join(json_dir, f'anomaly_{anomaly_id}.json')
            with open(json_file, 'w') as f:
                json.dump({
                    'id': anomaly_id,
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'duration': duration,
                    'type': anomaly_type,
                    'severity': severity,
                    'data': anomaly_data_buffer
                }, f)
            
            # Description
            description = f"Anomalie détectée: {anomaly_type}"
            if bpm_min and bpm_min < ANOMALY_BPM_MIN:
                description += f" | BPM bas: {bpm_min:.0f}"
            if bpm_max and bpm_max > ANOMALY_BPM_MAX:
                description += f" | BPM élevé: {bpm_max:.0f}"
            if max(accel_x_max, accel_y_max, accel_z_max) > ANOMALY_ACCEL_THRESHOLD:
                description += f" | Mouvement intense"
            
            # Écrire dans le fichier CSV
            with open(anomalies_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    start_time.isoformat(),
                    end_time.isoformat(),
                    f"{duration:.1f}",
                    anomaly_type,
                    f"{bpm_min:.0f}" if bpm_min else '',
                    f"{bpm_max:.0f}" if bpm_max else '',
                    f"{bpm_avg:.0f}" if bpm_avg else '',
                    f"{accel_x_max:.3f}",
                    f"{accel_y_max:.3f}",
                    f"{accel_z_max:.3f}",
                    severity,
                    description
                ])
            
            print(f"⚠️  ANOMALIE ENREGISTRÉE: {anomaly_type} | Durée: {duration:.1f}s | Sévérité: {severity}")
            print(f"   💾 Données sauvegardées: {json_file}")
            
            # Retourner l'anomalie pour broadcast
            return {
                'id': anomaly_id,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration': duration,
                'type': anomaly_type,
                'severity': severity,
                'bpm_min': bpm_min,
                'bpm_max': bpm_max,
                'bpm_avg': bpm_avg,
                'accel_max': max(accel_x_max, accel_y_max, accel_z_max),
                'description': description
            }
            
        except Exception as e:
            print(f"❌ Erreur sauvegarde anomalie: {e}")
            import traceback
            traceback.print_exc()
            return None


def udp_receiver_thread():
    """Thread UDP non-bloquant pour recevoir les données ESP32"""
    global stats, session_start_time
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((UDP_HOST, UDP_PORT))
    
    stats['udp_running'] = True
    stats['total_samples'] = 0
    session_start_time = datetime.now()
    print(f"📡 Thread UDP démarré sur {UDP_HOST}:{UDP_PORT}")
    print(f"⏰ Session démarrée: {session_start_time.strftime('%H:%M:%S')}")
    
    while True:
        try:
            data, addr = sock.recvfrom(4096)
            raw_data = data.decode('utf-8').strip()
            
            # Parser le JSON
            try:
                packet = json.loads(raw_data)
                print(f"✅ Paquet reçu de {addr}: {raw_data}")
            except json.JSONDecodeError:
                print(f"⚠️  JSON invalide de {addr}: {raw_data[:100]}")
                continue
            
            # Mise à jour des stats
            stats['packets_received'] += 1
            stats['total_samples'] = len(signal_buffer)
            stats['last_packet_time'] = datetime.now().isoformat()
            if session_start_time:
                stats['session_duration'] = (datetime.now() - session_start_time).total_seconds()
            
            # Extraction des données
            timestamp = packet.get('timestamp', datetime.now().isoformat())
            
            # ECG (Signal cardiaque brut) - L'ESP32 envoie 'signal'
            ecg_value = packet.get('signal') or packet.get('ecg')
            if ecg_value is not None:
                try:
                    ecg_value = int(ecg_value)
                    print(f"   ECG: {ecg_value}")
                except (ValueError, TypeError):
                    ecg_value = None
                    print(f"   ⚠️ ECG invalide")
            
            # BPM (40-180 ou None)
            bpm = validate_bpm(packet.get('bpm'))
            if bpm:
                print(f"   BPM: {bpm}")
            
            # Accéléromètre (±2.0g) - L'ESP32 envoie 'acc_x', 'acc_y', 'acc_z'
            accel_x = packet.get('acc_x') or packet.get('x', 0.0)
            accel_y = packet.get('acc_y') or packet.get('y', 0.0)
            accel_z = packet.get('acc_z') or packet.get('z', 0.0)
            
            # Limiter à ±2.0g
            accel_x = max(-2.0, min(2.0, float(accel_x)))
            accel_y = max(-2.0, min(2.0, float(accel_y)))
            accel_z = max(-2.0, min(2.0, float(accel_z)))
            print(f"   Accel: X={accel_x:.3f} Y={accel_y:.3f} Z={accel_z:.3f}")
            
            # RÉCEPTION DES ALERTES DEPUIS L'ESP32
            global anomaly_active, anomaly_start_time, anomaly_data
            
            # L'ESP32 envoie le champ "alert": true/false + données d'anomalie
            is_alert = packet.get('alert', False)
            
            if is_alert:
                # Classifier l'anomalie avec les données ESP32
                type_fr, severity, niveau_urgence, message, delai = classifier_anomalie(packet)
                
                print(f"\n{'='*70}")
                print(f"⚠️  ALERTE REÇUE DE L'ESP32")
                print(f"{'='*70}")
                print(format_anomaly_log(type_fr, severity, niveau_urgence, message, delai))
                print(f"   Type ESP32: {packet.get('anomaly_type', 'N/A')}")
                print(f"   Sévérité ESP32: {packet.get('anomaly_severity', 'N/A')}")
                if packet.get('bpm_valid'):
                    print(f"   BPM: {bpm:.0f} (valide)")
                if packet.get('signal_valid'):
                    print(f"   Signal qualité: {packet.get('signal_quality', 0):.2f}")
                print(f"{'='*70}\n")
                
                if not anomaly_active:
                    # Début d'une nouvelle anomalie
                    anomaly_active = True
                    anomaly_start_time = datetime.now()
                    anomaly_data = []
                    print(f"\n🚨 DÉBUT ANOMALIE: {type_fr} | Sévérité: {severity.upper()}")
                    print(f"   Niveau urgence: {niveau_urgence}")
                    print(f"   Message: {message}")
                    
                    # Broadcaster alerte immédiate avec toutes les infos
                    socketio.emit('anomaly_alert', {
                        'type': type_fr,
                        'type_esp32': packet.get('anomaly_type', 'N/A'),
                        'severity': severity,
                        'severity_esp32': packet.get('anomaly_severity', 'N/A'),
                        'niveau_urgence': niveau_urgence,
                        'message': message,
                        'delai_intervention': delai,
                        'bpm': bpm,
                        'bpm_valid': packet.get('bpm_valid', False),
                        'accel_max': max(abs(accel_x), abs(accel_y), abs(accel_z)),
                        'signal_quality': packet.get('signal_quality', 0),
                        'timestamp': anomaly_start_time.isoformat()
                    }, namespace='/')
                
                # Accumuler les données de l'anomalie
                anomaly_data.append({
                    'timestamp': timestamp,
                    'ecg': ecg_value,
                    'bpm': bpm,
                    'accel_x': accel_x,
                    'accel_y': accel_y,
                    'accel_z': accel_z,
                    'anomaly_type': type_fr,
                    'anomaly_type_esp32': packet.get('anomaly_type', 'N/A'),
                    'severity': severity,
                    'severity_esp32': packet.get('anomaly_severity', 'N/A'),
                    'niveau_urgence': niveau_urgence,
                    'message': message,
                    'delai_intervention': delai,
                    'bpm_valid': packet.get('bpm_valid', False),
                    'signal_valid': packet.get('signal_valid', False),
                    'signal_quality': packet.get('signal_quality', 0)
                })
            else:
                if anomaly_active:
                    # Fin de l'anomalie
                    anomaly_end_time = datetime.now()
                    duration = (anomaly_end_time - anomaly_start_time).total_seconds()
                    
                    # Sauvegarder seulement si durée >= ANOMALY_MIN_DURATION
                    if duration >= ANOMALY_MIN_DURATION:
                        saved_anomaly = save_anomaly(anomaly_start_time, anomaly_end_time, anomaly_data)
                        if saved_anomaly:
                            # Broadcaster la fin de l'anomalie
                            socketio.emit('anomaly_end', saved_anomaly, namespace='/')
                        print(f"✅ FIN ANOMALIE | Durée: {duration:.1f}s")
                    else:
                        print(f"⏭️  Anomalie ignorée (durée < {ANOMALY_MIN_DURATION}s)")
                    
                    anomaly_active = False
                    anomaly_start_time = None
                    anomaly_data = []
            
            # Préparer les données pour broadcast
            data_packet = {
                'timestamp': timestamp,
                'ecg': ecg_value,
                'bpm': bpm,
                'accel': {
                    'x': round(accel_x, 3),
                    'y': round(accel_y, 3),
                    'z': round(accel_z, 3)
                }
            }
            
            # Ajouter aux buffers
            if ecg_value is not None:
                signal_buffer.append({
                    'time': timestamp,
                    'value': ecg_value,
                    'bpm': bpm
                })
            
            accel_buffer.append({
                'time': timestamp,
                'x': accel_x,
                'y': accel_y,
                'z': accel_z
            })
            
            # Broadcaster via WebSocket
            socketio.emit('sensor_data', data_packet, namespace='/')
            print(f"📤 Données envoyées via WebSocket")
            
            # Broadcaster les stats toutes les 10 paquets
            if stats['packets_received'] % 10 == 0:
                socketio.emit('stats_update', {
                    'total_samples': stats['total_samples'],
                    'session_duration': stats.get('session_duration', 0),
                    'packets_received': stats['packets_received']
                }, namespace='/')
            
            # Logger dans CSV si activé
            if csv_logging:
                log_to_csv({
                    'timestamp': timestamp,
                    'ecg': ecg_value or '',
                    'bpm': bpm or '',
                    'accel_x': accel_x,
                    'accel_y': accel_y,
                    'accel_z': accel_z
                })
            
            # Afficher résumé
            bpm_str = f"{bpm:.0f}" if bpm else "--"
            ecg_str = str(ecg_value) if ecg_value else "--"
            print(f"📊 Paquet #{stats['packets_received']} | "
                  f"BPM: {bpm_str} | "
                  f"ECG: {ecg_str} | "
                  f"Accel: X={accel_x:.2f} Y={accel_y:.2f} Z={accel_z:.2f}")
            print()
        
        except Exception as e:
            print(f"❌ Erreur UDP: {e}")
            import traceback
            traceback.print_exc()


@app.route('/')
def index():
    """Page principale"""
    return render_template('index.html')


@app.route('/download/data')
def download_data():
    """Télécharger le dernier fichier CSV de données"""
    try:
        # Trouver le fichier CSV le plus récent
        import glob
        csv_files = glob.glob('data_esp32_*.csv')
        if not csv_files:
            return "Aucun fichier de données disponible", 404
        
        # Trier par date de modification (le plus récent en premier)
        latest_file = max(csv_files, key=os.path.getmtime)
        
        from flask import send_file
        return send_file(latest_file, as_attachment=True, download_name=os.path.basename(latest_file))
    except Exception as e:
        print(f"❌ Erreur téléchargement données: {e}")
        return f"Erreur: {str(e)}", 500


@app.route('/download/anomalies')
def download_anomalies():
    """Télécharger le fichier CSV des anomalies"""
    try:
        if not os.path.exists(anomalies_file):
            return "Aucun fichier d'anomalies disponible", 404
        
        from flask import send_file
        return send_file(anomalies_file, as_attachment=True, download_name='anomalies_log.csv')
    except Exception as e:
        print(f"❌ Erreur téléchargement anomalies: {e}")
        return f"Erreur: {str(e)}", 500


@app.route('/api/anomaly/<anomaly_id>')
def get_anomaly_data(anomaly_id):
    """Récupérer les données d'une anomalie pour visualisation"""
    try:
        from flask import jsonify
        json_file = f'anomalies_data/anomaly_{anomaly_id}.json'
        
        if not os.path.exists(json_file):
            return jsonify({'error': 'Anomalie non trouvée'}), 404
        
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        return jsonify(data)
    except Exception as e:
        print(f"❌ Erreur récupération anomalie: {e}")
        from flask import jsonify
        return jsonify({'error': str(e)}), 500


@socketio.on('connect')
def handle_connect():
    """Nouveau client connecté"""
    print(f"✅ Client connecté: {request.sid}")
    
    # Envoyer TOUT l'historique (limité à 3000 derniers points pour le chargement initial)
    max_initial_load = 3000  # 5 minutes à 10Hz
    signal_list = list(signal_buffer)
    accel_list = list(accel_buffer)
    
    emit('history', {
        'signal': signal_list[-max_initial_load:] if len(signal_list) > max_initial_load else signal_list,
        'accel': accel_list[-max_initial_load:] if len(accel_list) > max_initial_load else accel_list,
        'total_samples': len(signal_list),
        'session_start': session_start_time.isoformat() if session_start_time else None
    })
    
    # Envoyer le statut
    emit('status', stats)


@socketio.on('disconnect')
def handle_disconnect():
    """Client déconnecté"""
    print(f"❌ Client déconnecté")


@socketio.on('start_csv')
def handle_start_csv():
    """Démarrer l'enregistrement CSV"""
    filename = start_csv_logging()
    emit('csv_status', {'recording': True, 'filename': filename})
    socketio.emit('csv_status', {'recording': True, 'filename': filename}, broadcast=True)


@socketio.on('stop_csv')
def handle_stop_csv():
    """Arrêter l'enregistrement CSV"""
    stop_csv_logging()
    emit('csv_status', {'recording': False, 'filename': None})
    socketio.emit('csv_status', {'recording': False, 'filename': None}, broadcast=True)


@socketio.on('get_status')
def handle_get_status():
    """Retourner les statistiques"""
    emit('status', stats)


@socketio.on('get_anomalies')
def handle_get_anomalies():
    """Retourner l'historique des anomalies"""
    try:
        anomalies = []
        if os.path.exists(anomalies_file):
            with open(anomalies_file, 'r') as f:
                reader = csv.DictReader(f)
                anomalies = list(reader)
        
        # Trier par date décroissante (plus récent en premier)
        anomalies.reverse()
        
        emit('anomalies_history', {'anomalies': anomalies[:50]})  # 50 dernières
    except Exception as e:
        print(f"❌ Erreur lecture anomalies: {e}")
        emit('anomalies_history', {'anomalies': []})


@socketio.on('clear_anomalies')
def handle_clear_anomalies():
    """Effacer l'historique des anomalies (nécessite confirmation)"""
    try:
        # Créer un backup
        if os.path.exists(anomalies_file):
            backup_name = f"anomalies_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            os.rename(anomalies_file, backup_name)
            print(f"💾 Backup créé: {backup_name}")
        
        # Réinitialiser le fichier
        init_anomalies_log()
        emit('anomalies_cleared', {'success': True})
        print("🗑️  Historique des anomalies effacé")
    except Exception as e:
        print(f"❌ Erreur effacement anomalies: {e}")
        emit('anomalies_cleared', {'success': False, 'error': str(e)})


def get_local_ip():
    """Obtenir l'IP locale du Raspberry Pi"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"


if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 ESP32 REALTIME MONITOR - FLASK + SOCKET.IO")
    print("="*50)
    
    # Initialiser le système d'anomalies
    init_anomalies_log()
    print("⚠️  Système de réception d'alertes activé (ESP32)")
    print("   Format attendu: {\"alert\": true/false}")
    print(f"   Seuils analyse: BPM: {ANOMALY_BPM_MIN}-{ANOMALY_BPM_MAX} | Accel: {ANOMALY_ACCEL_THRESHOLD}g")
    
    # Démarrer le thread UDP avec eventlet
    eventlet.spawn(udp_receiver_thread)
    
    # Afficher les infos de connexion
    local_ip = get_local_ip()
    print(f"\n📡 Serveur UDP: {UDP_HOST}:{UDP_PORT}")
    print(f"🌐 Interface Web: http://{local_ip}:5000")
    print(f"� Stockage: ILLIMITÉ (toutes les données conservées en mémoire)")
    print(f"\n✨ Serveur prêt! Ouvrez http://{local_ip}:5000 dans votre navigateur\n")
    
    # Lancer Flask-SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
