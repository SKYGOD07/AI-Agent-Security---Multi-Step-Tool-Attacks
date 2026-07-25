import json
from pathlib import Path

class NotebookBuilder:
    """Compiles Blueprint nodes into a functional Jupyter Notebook."""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir

    def build_from_nodes(self, nodes: list, version_name: str) -> dict:
        """Translates a graph of nodes into a sequence of code cells."""
        notebook = {
            "cells": [],
            "metadata": {
                "language_info": {
                    "name": "python"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 5
        }
        
        # Simple topological sort/linearizer for demo
        sorted_nodes = sorted(nodes, key=lambda n: n.get("x", 0))
        
        for node in sorted_nodes:
            label = node.get("label", "Unknown")
            data = node.get("data", {})
            
            # Generate cell content based on node type
            source = [f"# --- Blueprint Node: {label} ---\n"]
            
            if node.get("type") == "event":
                source.append("import pandas as pd\nimport numpy as np\n")
                source.append('print("Starting execution...")\n')
            
            elif node.get("type") == "ai":
                prompt = data.get("prompt", "")
                source.append(f'# LLM Prompt Logic\nprompt = """{prompt}"""\n')
                source.append('# TODO: Insert LLM call here\n')
                
            else:
                for k, v in data.items():
                    source.append(f"{k} = {repr(v)}\n")
            
            notebook["cells"].append({
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": source
            })
            
        out_dir = self.project_dir / "versions" / version_name
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "generated_notebook.ipynb"
        
        out_path.write_text(json.dumps(notebook, indent=2), encoding="utf-8")
        return {"success": True, "path": str(out_path)}
