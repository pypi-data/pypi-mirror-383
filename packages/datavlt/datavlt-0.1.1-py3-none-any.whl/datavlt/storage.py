import json
import os
import csv
import sqlite3

class DataStorage:
    def __init__(self, filename='datavit_data.json', mode='json'):
        self.filename = filename
        self.mode = mode
        self.data = []

    def load(self):
        if not os.path.exists(self.filename):
            self.data = []
            return

        if self.mode == 'json':
            with open(self.filename, 'r') as f:
                self.data = json.load(f)
        elif self.mode == 'csv':
            with open(self.filename, 'r', newline='') as f:
                reader = csv.DictReader(f)
                self.data = list(reader)
        elif self.mode == 'sqlite':
            conn = sqlite3.connect(self.filename)
            cursor = conn.execute("SELECT name, age FROM data")
            self.data = [{"name": row[0], "age": row[1]} for row in cursor.fetchall()]
            conn.close()

    def save(self):
        if self.mode == 'json':
            with open(self.filename, 'w') as f:
                json.dump(self.data, f, indent=2)
        elif self.mode == 'csv':
            if not self.data:
                return
            with open(self.filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.data[0].keys())
                writer.writeheader()
                writer.writerows(self.data)
        elif self.mode == 'sqlite':
            conn = sqlite3.connect(self.filename)
            conn.execute("CREATE TABLE IF NOT EXISTS data (name TEXT, age INTEGER)")
            conn.execute("DELETE FROM data")
            for row in self.data:
                conn.execute("INSERT INTO data VALUES (?, ?)", (row['name'], row['age']))
            conn.commit()
            conn.close()

    def add(self, record: dict):
        self.data.append(record)
        self.save()

    def get_all(self):
        return self.data

    def clear(self):
        self.data = []
        self.save()

    def add_unique(self, record: dict):
        if record not in self.data:
            self.data.append(record)
            self.save()