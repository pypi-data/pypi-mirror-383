from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import json
import os

from datavit.storage import DataStorage
from datavit.processor import DataProcessor
from datavit.validator import validate_record

# Загружаем токен
if os.path.exists("config.json"):
    with open("config.json", "r") as f:
        CONFIG = json.load(f)
else:
    CONFIG = {"api_key": "SECRET123"}

storage = DataStorage()
storage.load()

class DataHandler(BaseHTTPRequestHandler):
    def _check_auth(self):
        api_key = self.headers.get("Authorization")
        if api_key != f"Bearer {CONFIG['api_key']}":
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'{"error": "Unauthorized"}')
            return False
        return True

    def _send_json(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def do_GET(self):
        if not self._check_auth():
            return

        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)

        # отдаём веб-интерфейс
        if parsed.path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open("web/index.html", "r", encoding="utf-8") as f:
                self.wfile.write(f.read().encode())
            return

        if parsed.path == '/data':
            self._send_json(storage.get_all())
        elif parsed.path == '/filter':
            key = query.get('key', [''])[0]
            value = query.get('value', [''])[0]
            processor = DataProcessor(storage.get_all())
            result = processor.filter_by_key(key, value)
            self._send_json(result)
        else:
            self._send_json({'error': 'Invalid endpoint'}, 404)

    def do_POST(self):
        if not self._check_auth():
            return

        if self.path == '/data':
            length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(length))

            if not validate_record(data):
                self._send_json({"error": "Invalid data format"}, 400)
                return

            storage.add_unique(data)
            self._send_json({"status": "record added"})

def run_http_server(port=8000):
    server = HTTPServer(('localhost', port), DataHandler)
    print(f"✅ Server running at http://localhost:{port}")
    print(f"Use header: Authorization: Bearer {CONFIG['api_key']}")
    server.serve_forever()
