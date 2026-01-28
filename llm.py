"""
LLM Interface
Handles communication with Ollama for local LLM inference.
"""

import requests
import json
from typing import Optional

OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "mistral:7b-instruct"

class LLMClient:
    """Client for interacting with Ollama API."""
    
    def __init__(self, model: str = DEFAULT_MODEL, base_url: str = OLLAMA_BASE_URL):
        self.model = model
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
    
    def generate(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> Optional[str]:
        """
        Generate response from LLM.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        
        Returns:
            Generated text or None if error
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
        except requests.exceptions.ConnectionError:
            print(f"❌ Error: Cannot connect to Ollama at {self.base_url}")
            print("   Make sure Ollama is running: ollama serve")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Error calling Ollama API: {e}")
            return None
    
    def check_connection(self) -> bool:
        """Check if Ollama is running and model is available."""
        try:
            # Check if Ollama is running
            health_url = f"{self.base_url}/api/tags"
            response = requests.get(health_url, timeout=5)
            response.raise_for_status()
            
            # Check if model exists
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            
            if self.model not in model_names:
                print(f"⚠️  Model '{self.model}' not found in Ollama.")
                print(f"   Available models: {', '.join(model_names) if model_names else 'None'}")
                print(f"   Install with: ollama pull {self.model}")
                return False
            
            return True
        except requests.exceptions.RequestException:
            return False

def get_llm_client(model: str = DEFAULT_MODEL) -> LLMClient:
    """Factory function to get LLM client."""
    return LLMClient(model=model)



