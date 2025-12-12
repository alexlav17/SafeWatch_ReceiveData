def validate_sensor_data(data):
    if not isinstance(data, dict):
        raise ValueError("Data must be a dictionary.")
    
    required_keys = ['id', 'type', 'x', 'y', 'z']
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing required key: {key}")
    # vérifie les types simples
    try:
        float(data['x'])
        float(data['y'])
        float(data['z'])
    except Exception:
        raise ValueError("x, y and z must be numeric.")
    return True

def process_sensor_data(data):
    validate_sensor_data(data)
    # conversion simple / normalisation si nécessaire
    return {
        "id": str(data['id']),
        "type": str(data['type']),
        "x": float(data['x']),
        "y": float(data['y']),
        "z": float(data['z']),
        "processed": True
    }