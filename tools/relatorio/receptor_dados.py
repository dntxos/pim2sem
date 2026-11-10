"""Recebe, via POST, séries de dados enviadas pelo simulador (console do navegador) e grava em disco.

Uso: python3 tools/relatorio/receptor_dados.py docs/relatorio/dados
No console do simulador: fetch('http://127.0.0.1:8001/nome.json', {method:'POST', body: JSON.stringify(obj)})
"""
import http.server
import os
import sys

DIR = sys.argv[1] if len(sys.argv) > 1 else '.'


class Receptor(http.server.BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')

    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()

    def do_POST(self):
        corpo = self.rfile.read(int(self.headers['Content-Length']))
        nome = os.path.basename(self.path.strip('/')) or 'dados.json'
        with open(os.path.join(DIR, nome), 'wb') as f:
            f.write(corpo)
        self.send_response(200); self._cors(); self.end_headers(); self.wfile.write(b'ok')

    def log_message(self, *a):
        pass


http.server.HTTPServer(('127.0.0.1', 8001), Receptor).serve_forever()
