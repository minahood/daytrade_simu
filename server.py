#!/usr/bin/env python3
"""daytrade_simu 用ローカルプロキシサーバー（Python 標準ライブラリのみ）

起動:
    python3 server.py

ブラウザで開く:
    http://localhost:8765/index.html
"""
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import urlopen, Request
from urllib.parse import parse_qs, unquote

PORT = 8765
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/124.0.0.0 Safari/537.36'
    ),
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parts = self.path.split('?', 1)
        endpoint = parts[0]

        if endpoint == '/health':
            self._send(200, b'ok', 'text/plain')

        elif endpoint == '/proxy':
            qs = parse_qs(parts[1]) if len(parts) > 1 else {}
            url = unquote(qs.get('url', [''])[0])
            if not url:
                self._send(400, b'url parameter required', 'text/plain')
                return
            try:
                req = Request(url, headers=HEADERS)
                with urlopen(req, timeout=12) as resp:
                    body = resp.read()
                    ct = resp.headers.get('Content-Type', 'application/octet-stream')
                self._send(200, body, ct)
            except Exception as e:
                self._send(502, str(e).encode('utf-8'), 'text/plain')

        else:
            # index.html を配信（それ以外のパスも含む）
            try:
                with open(os.path.join(BASE_DIR, 'index.html'), 'rb') as f:
                    self._send(200, f.read(), 'text/html; charset=utf-8')
            except FileNotFoundError:
                self._send(404, b'index.html not found', 'text/plain')

    def _send(self, code, body, ct):
        self.send_response(code)
        self.send_header('Content-Type', ct)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass  # アクセスログを抑制


if __name__ == '__main__':
    server = HTTPServer(('localhost', PORT), Handler)
    print(f'ローカルプロキシサーバー起動中 → http://localhost:{PORT}/')
    print(f'アプリを開く              → http://localhost:{PORT}/index.html')
    print('停止するには Ctrl+C を押してください')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nサーバーを停止しました')
