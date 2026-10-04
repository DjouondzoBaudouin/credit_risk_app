"""
Serveur HTTP local minimaliste pour l'application d'analyse de risque de crédit.
Utilise la bibliothèque standard http.server pour éviter les frameworks lourds.
Gère les fichiers statiques et les requêtes API JSON/multipart.
"""
import http.server
import socketserver
import json
import os
import re
import email
from urllib.parse import urlparse, parse_qs
import sys

# Ajout du chemin racine pour les imports backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.data_manager import load_data, clean_data, map_columns, save_data, get_data_info
from backend.analysis import (
    get_descriptive_stats, get_gaussian_analysis, get_poisson_analysis,
    get_simple_regression, get_multiple_regression, get_logistic_regression
)
from backend.export import generate_excel_report
from generate_sample_data import generate_sample_dataset

PORT = 8000
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), 'frontend')
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')

class CustomHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        # Journalisation personnalisée pour l'interface
        print(f"[SERVER LOG] {args[0]}")

    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # Routes API GET
        if path == '/api/data_info':
            self.send_json_response(get_data_info())
            return

        # Servir les fichiers statiques
        if path == '/':
            path = '/index.html'
        
        file_path = os.path.normpath(os.path.join(FRONTEND_DIR, path.lstrip('/')))
        
        # Sécurité : empêcher l'accès en dehors du dossier frontend
        if not file_path.startswith(FRONTEND_DIR):
            self.send_error(403, "Accès interdit")
            return

        if os.path.isfile(file_path):
            self.send_response(200)
            ext = os.path.splitext(file_path)[1].lower()
            content_types = {
                '.html': 'text/html',
                '.css': 'text/css',
                '.js': 'application/javascript',
                '.json': 'application/json',
                '.csv': 'text/csv',
                '.png': 'image/png',
                '.jpg': 'image/jpeg'
            }
            self.send_header('Content-Type', content_types.get(ext, 'application/octet-stream'))
            self.send_cors_headers()
            self.end_headers()
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, "Fichier non trouvé")

    def do_POST(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        content_length = int(self.headers.get('Content-Length', 0))
        content_type = self.headers.get('Content-Type', '')

        try:
            if path == '/api/upload':
                self.handle_upload(content_length, content_type)
            elif path == '/api/generate':
                self.handle_generate()
            elif path == '/api/analyze':
                self.handle_analyze(content_length)
            elif path == '/api/export':
                self.handle_export(content_length)
            else:
                self.send_error(404, "Endpoint non trouvé")
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)

    def handle_upload(self, content_length, content_type):
        body = self.rfile.read(content_length)
        
        if 'multipart/form-data' in content_type:
            boundary = re.search(r'boundary=(.+)', content_type).group(1).strip('"')
            msg = email.message_from_bytes(b'Content-Type: multipart/form-data; boundary=' + boundary.encode() + b'\n\n' + body)
            
            file_data = None
            for part in msg.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                if part.get_filename():
                    file_data = {
                        'filename': part.get_filename(),
                        'content': part.get_payload(decode=True)
                    }
                    break
            
            if not file_data:
                self.send_json_response({'error': 'Aucun fichier trouvé'}, 400)
                return

            # Sauvegarde temporaire
            filepath = os.path.join(DATA_DIR, 'uploaded_data.csv')
            with open(filepath, 'wb') as f:
                f.write(file_data['content'])
            
            # Chargement et nettoyage
            df = load_data(filepath)
            df = map_columns(df)
            df = clean_data(df)
            
            # Sauvegarde propre
            clean_path = os.path.join(DATA_DIR, 'credit_bancaire.csv')
            save_data(df, clean_path)
            
            self.send_json_response({
                'message': 'Fichier chargé et nettoyé avec succès',
                'info': get_data_info()
            })
        else:
            self.send_json_response({'error': 'Type de contenu non supporté'}, 400)

    def handle_generate(self):
        generate_sample_dataset()
        self.send_json_response({
            'message': 'Données simulées générées avec succès',
            'info': get_data_info()
        })

    def handle_analyze(self, content_length):
        body = self.rfile.read(content_length).decode('utf-8')
        payload = json.loads(body)
        task = payload.get('task')
        
        df = load_data(os.path.join(DATA_DIR, 'credit_bancaire.csv'))
        
        if task == 'descriptive':
            result = get_descriptive_stats(df)
        elif task == 'gaussian':
            result = get_gaussian_analysis(df)
        elif task == 'poisson':
            result = get_poisson_analysis(df)
        elif task == 'regression_simple':
            result = get_simple_regression(df, payload.get('prediction_value', 750000))
        elif task == 'regression_multiple':
            result = get_multiple_regression(df)
        elif task == 'logistic':
            result = get_logistic_regression(df)
        elif task == 'dashboard':
            result = get_descriptive_stats(df) # Simplifié pour le dashboard, peut être étendu
        else:
            self.send_json_response({'error': 'Tâche inconnue'}, 400)
            return
            
        self.send_json_response(result)

    def handle_export(self, content_length):
        body = self.rfile.read(content_length).decode('utf-8')
        payload = json.loads(body)
        
        df = load_data(os.path.join(DATA_DIR, 'credit_bancaire.csv'))
        output_path = os.path.join(OUTPUT_DIR, 'rapport_complet.xlsx')
        
        generate_excel_report(df, output_path)
        
        self.send_json_response({
            'message': 'Rapport Excel généré avec succès',
            'filepath': output_path
        })

    def send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode('utf-8'))

if __name__ == '__main__':
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"Serveur démarré sur http://localhost:{PORT}")
        print("Appuyez sur Ctrl+C pour arrêter.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nArrêt du serveur...")
            httpd.server_close()