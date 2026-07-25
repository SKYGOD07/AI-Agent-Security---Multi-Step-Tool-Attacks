"""
ROS Local Gateway Server (Phase 2).
Provides REST endpoints for the UE5 Blueprint Visual Editor.
Supports: Projects, Notebook parsing via LLM, Code generation, and AI generation.
"""
import json
import sys
import os
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT / "src"))

from ros.memory.graph import CausalGraph
from ros.planner.roadmap import DecisionIntelligence
from ros.context.project import ProjectManager
from ros.notebook.builder import NotebookBuilder
from ros.writeup.generator import WriteupGenerator

# Global Project Manager
pm = ProjectManager(str(WORKSPACE_ROOT))

class ROSGatewayHandler(BaseHTTPRequestHandler):

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
            self._json_response(200, {
                "service": "ROS Local Gateway",
                "status": "online",
                "active_project": pm.get_active_project()
            })

        elif path in ("/health", "/api/health"):
            ollama_ok = self._check_ollama()
            self._json_response(200, {
                "status": "online",
                "ollama_available": ollama_ok,
                "active_project": pm.get_active_project()
            })
            
        elif path == "/api/project/list":
            self._json_response(200, {"projects": pm.list_projects()})

        elif path == "/api/project/active":
            proj = pm.get_active_project()
            self._json_response(200, {"active_project": proj})

        elif path == "/api/graph":
            graph = CausalGraph(str(WORKSPACE_ROOT)) # Need to update CausalGraph to use project path later
            self._json_response(200, graph.export_ui_graph())

        elif path == "/api/roadmap":
            planner = DecisionIntelligence(str(WORKSPACE_ROOT))
            self._json_response(200, {"roadmap": planner.get_priority_roadmap()})

        else:
            self._json_response(404, {"error": "Not Found"})

    # ------------------------------------------------------------------ POST
    def do_POST(self):
        path = self.path.split("?")[0]

        if path == "/api/project/create":
            body = self._read_body()
            res = pm.create_project(body.get("name", ""), body.get("context", ""))
            self._json_response(200 if "success" in res else 400, res)
            
        elif path == "/api/project/load":
            body = self._read_body()
            res = pm.load_project(body.get("name", ""))
            self._json_response(200 if "success" in res else 400, res)

        elif path == "/api/generate":
            self._handle_generate()
        elif path == "/api/save":
            self._handle_save()
        elif path == "/api/analyze-notebook":
            self._handle_analyze_notebook()
        elif path == "/api/create-notebook":
            self._handle_create_notebook()
        elif path == "/api/writeup":
            self._handle_writeup()
        else:
            self._json_response(404, {"error": "Not Found"})

    # ------------------------------------------------------------------ Handlers
    def _handle_generate(self):
        body = self._read_body()
        prompt = body.get("prompt", "")
        system_prompt = body.get("system_prompt", None)
        
        if not prompt:
            self._json_response(400, {"error": "prompt is required"})
            return
            
        response_text = self._smart_generate(prompt, system_prompt)
        self._json_response(200, {"response": response_text, "provider": "auto"})

    def _smart_generate(self, prompt, system_prompt=None) -> str:
        if self._check_ollama():
            resp = self._call_ollama(prompt, system_prompt)
            if resp: return resp
            
        try:
            from ros.providers.cloud import ZhipuCloudProvider
            cloud = ZhipuCloudProvider()
            if cloud.is_available():
                return cloud.generate(prompt, system_prompt)
        except Exception:
            pass
        return "LLM Generation Error: Ollama is offline and GLM fallback failed."

    def _handle_save(self):
        body = self._read_body()
        version = body.get("version", "")
        manifest = body.get("manifest", None)
        code = body.get("code", None)
        
        proj_dir = pm.get_project_dir()
        if not proj_dir:
            self._json_response(400, {"error": "No active project"})
            return

        version_dir = proj_dir / "versions" / version
        version_dir.mkdir(parents=True, exist_ok=True)
        saved_files = []

        if manifest:
            p = version_dir / "manifest.yaml"
            p.write_text(manifest, encoding="utf-8")
            saved_files.append(str(p))

        if code:
            p = version_dir / f"attack_{version}.py"
            p.write_text(code, encoding="utf-8")
            saved_files.append(str(p))

        self._json_response(200, {"saved": True, "version": version, "files": saved_files})

    def _handle_analyze_notebook(self):
        body = self._read_body()
        notebook = body.get("notebook", {})
        
        cells = notebook.get("cells", [])
        code_extract = ""
        for i, cell in enumerate(cells):
            if cell.get("cell_type") == "code":
                code_extract += f"--- Cell {i} ---\n"
                code_extract += "".join(cell.get("source", [])) + "\n\n"
                
        system_prompt = "You are a code analyzer. Extract the distinct algorithmic steps from this code. Return ONLY valid JSON format: {\"nodes\": [{\"id\":\"n1\", \"type\":\"function\", \"label\":\"Step Name\", \"x\":200, \"y\":150, \"pins\":{\"in\":[{\"name\":\"Exec\",\"kind\":\"exec\"}], \"out\":[{\"name\":\"Exec\",\"kind\":\"exec\"}]}, \"data\":{\"info\":\"...\"}}]}"
        prompt = f"Extract the logic from this Kaggle notebook into blueprint nodes:\n{code_extract}"
        
        llm_resp = self._smart_generate(prompt, system_prompt)
        
        # Try to parse the JSON output from LLM
        nodes = []
        try:
            # Simple regex/find to extract json if it's wrapped in markdown ```json ... ```
            import re
            match = re.search(r'```json\s*(\{.*?\})\s*```', llm_resp, re.DOTALL)
            if match:
                parsed = json.loads(match.group(1))
            else:
                parsed = json.loads(llm_resp)
            nodes = parsed.get("nodes", [])
        except Exception as e:
            print("Failed to parse LLM JSON:", e)
            # Fallback to simple parser if LLM output isn't perfect JSON
            nodes.append({
                "id": "n_error", "type": "event", "label": "LLM Parsing Failed",
                "x": 200, "y": 150, "data": {"raw": llm_resp}
            })
            
        self._json_response(200, {"nodes": nodes})

    def _handle_create_notebook(self):
        body = self._read_body()
        nodes = body.get("nodes", [])
        proj_dir = pm.get_project_dir()
        
        if not proj_dir:
            self._json_response(400, {"error": "No active project"})
            return
            
        builder = NotebookBuilder(proj_dir)
        res = builder.build_from_nodes(nodes, "latest")
        self._json_response(200, {"message": f"Notebook created at {res['path']}"})

    def _handle_writeup(self):
        body = self._read_body()
        context = body.get("context", "")
        proj_dir = pm.get_project_dir()
        
        if not proj_dir:
            self._json_response(400, {"error": "No active project"})
            return
            
        gen = WriteupGenerator(proj_dir)
        writeup = gen.generate(context, self._smart_generate)
        self._json_response(200, {"writeup": writeup})


    # ------------------------------------------------------------------ LLM Utils
    def _check_ollama(self):
        import urllib.request
        try:
            req = urllib.request.Request(os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434") + "/api/tags", method="GET")
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
            return ""

    def log_message(self, fmt, *args):
        pass # Quiet


def run_server(port=8022):
    httpd = HTTPServer(("127.0.0.1", port), ROSGatewayHandler)
    print(f"ROS Gateway (Phase 2) live: http://127.0.0.1:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
