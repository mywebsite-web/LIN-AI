import http.server
import socketserver
import urllib.request
import json
import sys
import os

PORT = int(os.environ.get("PORT", "8000"))
HF_API_URL = "https://router.huggingface.co/v1/chat/completions"
HF_TOKEN = os.environ.get("HF_TOKEN", "")

class ProxyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Forward headers (specifically Authorization)
            headers = {
                'Content-Type': 'application/json',
                'Authorization': self.headers.get('Authorization', '') or (f"Bearer {HF_TOKEN}" if HF_TOKEN else '')
            }
            
            if not headers['Authorization']:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Missing token. Set HF_TOKEN environment variable on the server."}).encode('utf-8'))
                return
            
            req = urllib.request.Request(HF_API_URL, data=post_data, headers=headers, method='POST')
            
            try:
                with urllib.request.urlopen(req) as response:
                    response_body = response.read()
                    self.send_response(response.status)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(response_body)
            except urllib.error.HTTPError as e:
                self.send_response(e.code)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(e.read())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                error_msg = json.dumps({"error": str(e)}).encode('utf-8')
                self.wfile.write(error_msg)
        else:
            self.send_error(404, "File not found")

Handler = ProxyHTTPRequestHandler

print(f"Serving on port {PORT} with proxy to {HF_API_URL}")
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
