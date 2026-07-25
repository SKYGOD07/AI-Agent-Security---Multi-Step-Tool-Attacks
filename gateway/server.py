import json
import sys
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

# Add workspace to import path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ros.memory.graph import CausalGraph
from ros.planner.roadmap import DecisionIntelligence
from ros.providers.router import LLMRouter

class ROSGatewayHandler(BaseHTTPRequestHandler):
    """Zero-dependency Local Gateway Server HTTP Handler."""
    
    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0]
        
        if path in ("/health", "/api/health"):
            router = LLMRouter()
            data = {
                "status": "online",
                "service": "ROS Local Gateway",
                "ollama_available": router.ollama.is_available()
            }
            self._send_json_response(200, data)
            
        elif path == "/api/graph":
            graph = CausalGraph(".")
            self._send_json_response(200, graph.export_ui_graph())
            
        elif path == "/api/roadmap":
            planner = DecisionIntelligence(".")
            self._send_json_response(200, {"roadmap": planner.get_priority_roadmap()})
            
        elif path == "/api/dashboard":
            graph = CausalGraph(".")
            graph.load_versions()
            data = {
                "health": 84,
                "verified_knowledge": 61,
                "total_versions": len(graph.nodes),
                "best_baseline": "v20 (Compact Replay-Portfolio)",
                "next_experiment": "Replay Safe Margin Tuning (+2.5 gain)"
            }
            self._send_json_response(200, data)
            
        else:
            self._send_json_response(404, {"error": "Not Found"})

    def _send_json_response(self, code: int, payload: dict):
        self.send_response(code)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))

def run_server(port=8022):
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, ROSGatewayHandler)
    print(f"ROS Local Gateway Server running on http://127.0.0.1:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
