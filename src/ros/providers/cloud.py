import os
import time
import json
import urllib.request
import hmac
import hashlib
import base64
from pathlib import Path
from ros.providers.base import BaseLLMProvider

class ZhipuCloudProvider(BaseLLMProvider):
    """
    Cloud LLM Provider targeting Zhipu AI (GLM-4-Flash / GLM-4-Plus).
    Reads key safely from local_only/gateway_env.txt (un-tracked).
    """
    
    def __init__(self, api_key: str = None, model: str = "glm-4-flash"):
        self.api_key = api_key or os.getenv("ZHIPUAI_API_KEY")
        if not self.api_key:
            env_file = Path("local_only/gateway_env.txt")
            if env_file.exists():
                for line in env_file.read_text(encoding="utf-8").splitlines():
                    if line.startswith("ZHIPUAI_API_KEY="):
                        self.api_key = line.split("=", 1)[1].strip()
        self.model = model

    def is_available(self) -> bool:
        return bool(self.api_key and "." in self.api_key)

    def generate(self, prompt: str, system_prompt: str = None) -> str:
        if not self.is_available():
            return "GLM Cloud Provider Notice: API Key not configured in local_only/gateway_env.txt."
            
        try:
            from zhipuai import ZhipuAI
            client = ZhipuAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"GLM Cloud Model (Key Configured): {str(e)}"
