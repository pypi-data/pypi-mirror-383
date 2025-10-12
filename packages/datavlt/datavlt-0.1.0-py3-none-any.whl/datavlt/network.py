from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class DataHandler(BaseHTTPRequestHandler):
    data_source = []

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = json.dumps(self.data_source).encode()
        self.wfile.write(response)

def run_http_server(data, port=8000):
    DataHandler.data_source = data
    server = HTTPServer(('localhost', port), DataHandler)
    print(f"Server running at http://localhost:{port}")
    server.serve_forever()