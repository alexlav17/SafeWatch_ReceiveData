class Sensor:
    def __init__(self, sensor_id, sensor_type, value):
        self.id = sensor_id
        self.type = sensor_type
        self.value = value

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "value": self.value
        }