import os
from ros.providers.ollama import OllamaProvider

class LLMRouter:
    """
    Routes requests to the appropriate LLM Provider (Ollama by default).
    """
    
    def __init__(self):
        self.ollama = OllamaProvider()

    def get_provider(self, task_type: str = "general"):
        """Returns Ollama if available, or fallbacks."""
        if self.ollama.is_available():
            return self.ollama
        return self.ollama  # Defaults to Ollama handler

    def query(self, prompt: str, system_prompt: str = None) -> str:
        provider = self.get_provider()
        return provider.generate(prompt, system_prompt)

if __name__ == "__main__":
    router = LLMRouter()
    print(f"Ollama available: {router.ollama.is_available()}")
