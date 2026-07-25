import json
import re
from pathlib import Path

class CausalGraph:
    """
    Real Graph Engine for the Research Operating System.
    Scans version directories for manifest.yaml files and experiment logs,
    building an in-memory graph and emitting UI-compatible node/edge arrays.
    """
    
    def __init__(self, workspace_root: str = "."):
        self.root = Path(workspace_root).resolve()
        self.versions_dir = self.root / "our_work" / "versions"
        self.log_file = self.root / "memory" / "experiment_log.jsonl"
        self.nodes = []
        self.edges = []

    def _parse_simple_yaml(self, filepath: Path) -> dict:
        """Simple regex-based YAML parser for manifest files."""
        data = {}
        if not filepath.exists():
            return data
        
        content = filepath.read_text(encoding="utf-8")
        current_key = None
        current_list = None
        
        for line in content.splitlines():
            line_str = line.strip()
            if not line_str or line_str.startswith("#"):
                continue
            
            # Match list items
            if line_str.startswith("- ") and current_list is not None:
                current_list.append(line_str[2:].strip())
                continue
                
            # Match key-value
            if ":" in line_str:
                parts = line_str.split(":", 1)
                key = parts[0].strip()
                val = parts[1].strip()
                
                if val:
                    # Remove quotes
                    val = val.strip("\"'")
                    data[key] = val
                    current_list = None
                else:
                    data[key] = []
                    current_list = data[key]
                    
        return data

    def load_versions(self):
        """Scans the repository to load all version manifests and builds nodes and edges."""
        self.nodes = []
        self.edges = []
        
        if not self.versions_dir.exists():
            return

        for v_dir in sorted(self.versions_dir.glob("v*")):
            if not v_dir.is_dir():
                continue
            
            manifest_path = v_dir / "manifest.yaml"
            if manifest_path.exists():
                meta = self._parse_simple_yaml(manifest_path)
                v_name = meta.get("version", v_dir.name)
                score = meta.get("public_score", "unknown")
                status = meta.get("status", "unknown")
                parent = meta.get("parent", None)
                
                node = {
                    "id": v_name,
                    "type": "version",
                    "label": f"{v_name} ({score})",
                    "score": score,
                    "status": status,
                    "details": meta
                }
                self.nodes.append(node)
                
                if parent:
                    self.edges.append({
                        "source": parent,
                        "target": v_name,
                        "label": "parent"
                    })

    def export_ui_graph(self) -> dict:
        """Exports the graph in a digital diagram payload standard for UI visualizers."""
        self.load_versions()
        return {
            "nodes": self.nodes,
            "edges": self.edges,
            "summary": {
                "total_versions": len(self.nodes),
                "total_relationships": len(self.edges)
            }
        }

if __name__ == "__main__":
    graph = CausalGraph()
    print(json.dumps(graph.export_ui_graph(), indent=2))
