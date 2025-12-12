class Collector:
    def __init__(self):
        self.data = []

    def collect_data(self, sensor_data):
        self.data.append(sensor_data)

    def process_data(self):
        # Implement data processing logic here
        processed_data = []
        for data in self.data:
            # Example processing: just return the data as is
            processed_data.append(data)
        return processed_data

    def clear_data(self):
        self.data = []