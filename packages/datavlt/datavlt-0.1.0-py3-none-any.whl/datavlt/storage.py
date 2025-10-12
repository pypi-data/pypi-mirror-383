import json
import os

class DataStorage:
    def __init__(self, filename='dataflow_data.json'):
        self.filename = filename
        self.data = []

    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = []

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=2)

    def add(self, record: dict):
        self.data.append(record)
        self.save()

    def get_all(self):
        return self.data

    def clear(self):
        """Очищает все данные и файл."""
        self.data = []
        self.save()

    def add_unique(self, record: dict):
         if record not in self.data:
             self.data.append(record)
             self.save()
