def validate_sensor_data(data):
    if not isinstance(data, dict):
        raise ValueError("Data must be a dictionary.")
    
    # On accepte les données même si tous les champs ne sont pas présents
    # (certains paquets peuvent être accel only, d'autres heart only)
    return True

def process_sensor_data(data):
    validate_sensor_data(data)
    # Conversion simple / normalisation - extraire tous les champs disponibles
    processed = {
        "id": str(data.get('id', 'unknown')),
        "type": str(data.get('type', 'sensor')),
        "x": float(data.get('x', 0.0)),
        "y": float(data.get('y', 0.0)),
        "z": float(data.get('z', 0.0)),
        "processed": True
    }
    
    # Ajouter les données cardiaques si présentes
    if 'bpm' in data:
        processed['bpm'] = float(data['bpm'])
    if 'ir' in data:
        processed['ir'] = int(data['ir'])
    if 'ecg' in data:
        processed['ecg'] = int(data['ecg'])
    
    return processed