from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "status": "healthy",
            "message": "LLM Benchmark Framework API",
            "version": "1.0.0",
            "note": "Full Streamlit app works better on Streamlit Cloud"
        }
        
        self.wfile.write(json.dumps(response).encode())
        return 