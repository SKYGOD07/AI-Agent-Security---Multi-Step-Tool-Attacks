import json
import os
from pathlib import Path

class ProjectManager:
    """Manages the Project Workspaces for the ROS IDE."""
    
    def __init__(self, workspace_root: str):
        self.root = Path(workspace_root)
        self.projects_dir = self.root / "projects"
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self.active_project = None
        self._load_active()

    def _load_active(self):
        state_file = self.root / "local_only" / "active_project.txt"
        if state_file.exists():
            active = state_file.read_text().strip()
            if active and (self.projects_dir / active).exists():
                self.active_project = active

    def _save_active(self, name: str):
        self.active_project = name
        state_dir = self.root / "local_only"
        state_dir.mkdir(parents=True, exist_ok=True)
        (state_dir / "active_project.txt").write_text(name)

    def get_active_project(self) -> str:
        return self.active_project or ""

    def list_projects(self) -> list:
        return [d.name for d in self.projects_dir.iterdir() if d.is_dir()]

    def create_project(self, name: str, context: str) -> dict:
        if not name:
            return {"error": "Project name cannot be empty."}
        
        proj_dir = self.projects_dir / name
        if proj_dir.exists():
            return {"error": "Project already exists."}
            
        proj_dir.mkdir(parents=True)
        (proj_dir / "versions").mkdir()
        (proj_dir / "skills").mkdir()
        
        context_data = {
            "name": name,
            "description": context,
            "created_at": "now",
            "current_best_score": None,
            "active_hypothesis": None
        }
        
        (proj_dir / "project_context.json").write_text(json.dumps(context_data, indent=2))
        self._save_active(name)
        
        return {"success": True, "project": name}

    def load_project(self, name: str) -> dict:
        if not (self.projects_dir / name).exists():
            return {"error": "Project not found."}
        
        self._save_active(name)
        context_path = self.projects_dir / name / "project_context.json"
        
        if context_path.exists():
            return {"success": True, "project": name, "context": json.loads(context_path.read_text())}
        return {"success": True, "project": name, "context": {}}

    def get_project_dir(self, name: str = None) -> Path:
        target = name or self.active_project
        if not target:
            return None
        return self.projects_dir / target
