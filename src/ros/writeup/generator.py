import json
from pathlib import Path

class WriteupGenerator:
    """Generates Kaggle Writeups using LLM."""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir

    def generate(self, context_str: str, llm_generate_func) -> str:
        """Reads project context and generates writeup via injected LLM func."""
        project_context = ""
        context_file = self.project_dir / "project_context.json"
        if context_file.exists():
            project_context = context_file.read_text()
            
        system_prompt = (
            "You are an expert AI Kaggle Grandmaster. "
            "Your task is to write a comprehensive, professional first-place solution writeup "
            "for a Kaggle competition based on the provided project context and architecture graph."
        )
        
        prompt = f"Project Context:\n{project_context}\n\nAdditional Input:\n{context_str}\n\nPlease generate the Markdown writeup."
        
        response = llm_generate_func(prompt, system_prompt)
        
        # Fallback if LLM fails
        if not response or "error" in response.lower():
            response = (
                "# 1st Place Solution Writeup\n\n"
                "## Summary\n"
                "We built an automated ROS Blueprint to dynamically extract and trace paths.\n\n"
                "## Architecture\n"
                "Please check the connected nodes in the blueprint editor.\n"
            )
            
        return response
