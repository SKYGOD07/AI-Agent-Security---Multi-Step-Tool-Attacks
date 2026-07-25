from abc import ABC, abstractmethod

class BaseLLMProvider(ABC):
    """Abstract Base Class for ROS LLM Providers (Ollama, Cloud, etc.)."""
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass
