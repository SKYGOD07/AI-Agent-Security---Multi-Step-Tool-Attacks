"""
ROS Local Gateway Server.
Provides REST endpoints for the UE5 Blueprint Visual Editor.
Supports: graph queries, LLM generation (Ollama/GLM), and file saving to disk.
"""
import json
import sys
import os
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

# Add workspace src to import path
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT / "src"))

from ros.memory.graph import CausalGraph
from ros.planner.roadmap import DecisionIntelligence


class ROSGatewayHandler(BaseHTTPRequestHandler):
    """HTTP Handler for the ROS Local Gateway."""

    def _send_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json_response(self, code, payload):
        self.send_response(code)
        self._send_cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length)) if length else {}

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors()
        self.end_headers()

    # ------------------------------------------------------------------ GET
    def do_GET(self):
        path = self.path.split("?")[0]

        if path == "/" or path == "":
            # Root dashboard summary
            graph = CausalGraph(str(WORKSPACE_ROOT))
            graph.load_versions()
            self._json_response(200, {
                "service": "ROS Local Gateway",
                "status": "online",
                "versions_loaded": len(graph.nodes),
                "endpoints": [
                    "GET  /api/health",
                    "GET  /api/graph",
                    "GET  /api/roadmap",
                    "POST /api/generate",
                    "POST /api/save",
                ],
            })

        elif path in ("/health", "/api/health"):
            ollama_ok = self._check_ollama()
            self._json_response(200, {
                "status": "online",
                "service": "ROS Local Gateway",
                "ollama_available": ollama_ok,
                "workspace": str(WORKSPACE_ROOT),
            })

        elif path == "/api/graph":
            graph = CausalGraph(str(WORKSPACE_ROOT))
            self._json_response(200, graph.export_ui_graph())

        elif path == "/api/roadmap":
            planner = DecisionIntelligence(str(WORKSPACE_ROOT))
            self._json_response(200, {"roadmap": planner.get_priority_roadmap()})

        elif path == "/api/files":
            # List version directories and their files
            versions_dir = WORKSPACE_ROOT / "our_work" / "versions"
            listing = {}
            if versions_dir.exists():
                for d in sorted(versions_dir.glob("v*")):
                    if d.is_dir():
                        listing[d.name] = [f.name for f in d.iterdir() if f.is_file()]
            self._json_response(200, {"versions": listing})

        else:
            self._json_response(404, {"error": "Not Found"})

    # ------------------------------------------------------------------ POST
    def do_POST(self):
        path = self.path.split("?")[0]

        if path == "/api/generate":
            self._handle_generate()
        elif path == "/api/save":
            self._handle_save()
        else:
            self._json_response(404, {"error": "Not Found"})

    def _handle_generate(self):
        """Send a prompt to Ollama (local) or GLM-4 Cloud and return the response."""
        body = self._read_body()
        prompt = body.get("prompt", "")
        system_prompt = body.get("system_prompt", None)
        provider_name = body.get("provider", "auto")

        if not prompt:
            self._json_response(400, {"error": "prompt is required"})
            return

        # Try Ollama first, then GLM Cloud
        response_text = ""
        used_provider = ""

        if provider_name in ("auto", "ollama"):
            if self._check_ollama():
                response_text = self._call_ollama(prompt, system_prompt)
                used_provider = "ollama"

        if not response_text and provider_name in ("auto", "cloud"):
            try:
                from ros.providers.cloud import ZhipuCloudProvider
                cloud = ZhipuCloudProvider()
                if cloud.is_available():
                    response_text = cloud.generate(prompt, system_prompt)
                    used_provider = "glm-4-flash"
            except Exception as e:
                response_text = f"Cloud provider error: {e}"
                used_provider = "glm-4-flash (error)"

        if not response_text:
            response_text = "No LLM provider available. Start Ollama or configure GLM key."
            used_provider = "none"

        self._json_response(200, {
            "response": response_text,
            "provider": used_provider,
        })

    def _handle_save(self):
        """Save blueprint data to disk as manifest.yaml and/or attack code."""
        body = self._read_body()
        version = body.get("version", "")
        manifest = body.get("manifest", None)
        code = body.get("code", None)

        if not version:
            self._json_response(400, {"error": "version is required"})
            return

        version_dir = WORKSPACE_ROOT / "our_work" / "versions" / version
        version_dir.mkdir(parents=True, exist_ok=True)
        saved_files = []

        if manifest:
            manifest_path = version_dir / "manifest.yaml"
            manifest_path.write_text(manifest, encoding="utf-8")
            saved_files.append(str(manifest_path))

        if code:
            code_path = version_dir / f"attack_{version}.py"
            code_path.write_text(code, encoding="utf-8")
            saved_files.append(str(code_path))

        self._json_response(200, {
            "saved": True,
            "version": version,
            "files": saved_files,
        })

    # ------------------------------------------------------------------ Helpers
    def _check_ollama(self):
        import urllib.request
        try:
            req = urllib.request.Request(
                os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434") + "/api/tags",
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=1) as r:
                return r.status == 200
        except Exception:
            return False

    def _call_ollama(self, prompt, system_prompt=None):
        import urllib.request
        url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434") + "/api/generate"
        payload = {"model": "llama3", "prompt": prompt, "stream": False}
        if system_prompt:
            payload["system"] = system_prompt
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                result = json.loads(r.read().decode("utf-8"))
                return result.get("response", "")
        except Exception as e:
            return f"Ollama error: {e}"

    def log_message(self, fmt, *args):
        """Quieter logging."""
        sys.stderr.write(f"[GATEWAY] {args[0]} {args[1]}\n")


def run_server(port=8022):
    httpd = HTTPServer(("127.0.0.1", port), ROSGatewayHandler)
    print(f"ROS Gateway live: http://127.0.0.1:{port}")
    print(f"Workspace: {WORKSPACE_ROOT}")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()
