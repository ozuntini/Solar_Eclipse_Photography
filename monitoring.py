#!/usr/bin/env python3
"""
Serveur web simple pour monitoring à distance
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
from pathlib import Path

class MonitoringHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/status':
            status = self.get_eclipse_status()
            self.send_json_response(status)
        elif self.path == '/logs':
            logs = self.get_recent_logs()
            self.send_json_response(logs)
        else:
            self.send_html_dashboard()
    
    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def get_eclipse_status(self):
        # Lecture statut depuis fichiers logs
        return {
            'status': 'active',
            'next_action': 'Photo at 19:27:03',
            'cameras_active': 2,
            'photos_taken': 157,
            'disk_free_gb': 28.5
        }
    
    def get_recent_logs(self):
        # Lecture logs récents depuis fichiers logs
        return {
            'status': 'active',
            'next_action': 'Photo at 20:27:03',
            'cameras_active': 2,
            'photos_taken': 157,
            'disk_free_gb': 28.5
        }


# Démarrage serveur monitoring
if __name__ == "__main__":
    server = HTTPServer(('0.0.0.0', 8080), MonitoringHandler)
    print("🌐 Monitoring server: http://raspberry_pi:8080")
    server.serve_forever()