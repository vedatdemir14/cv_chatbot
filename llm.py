"""
LLM Interface
Handles communication with Groq's hosted inference API (OpenAI-compatible).

Groq is used instead of a local Ollama server so the backend can run fully
in the cloud (no local model server required). Get a free API key at
https://console.groq.com/keys and set it as the GROQ_API_KEY environment
variable.
"""

import os
import requests
from typing import Optional

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
# openai/gpt-oss-120b is currently Groq's flagship free production model
# (strongest general reasoning/quality on the free tier as of mid-2026).
# Override with the GROQ_MODEL env var, e.g. "llama-3.3-70b-versatile" as a
# fallback if you hit gpt-oss-120b's rate limit.
DEFAULT_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")


class LLMClient:
    """Client for interacting with the Groq chat completions API."""

    def __init__(self, model: str = DEFAULT_MODEL, base_url: str = GROQ_BASE_URL):
        self.model = model
        self.base_url = base_url
        self.api_url = f"{base_url}/chat/completions"
        self.api_key = os.getenv("GROQ_API_KEY")

    def generate(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> Optional[str]:
        """
        Generate a response from the LLM.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            Generated text or None if error
        """
        if not self.api_key:
            print("❌ Error: GROQ_API_KEY environment variable is not set.")
            print("   Get a free key at https://console.groq.com/keys")
            return None

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except requests.exceptions.ConnectionError:
            print(f"❌ Error: Cannot connect to Groq at {self.base_url}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Error calling Groq API: {e}")
            return None

    def check_connection(self) -> bool:
        """Check if the Groq API key is valid and reachable."""
        if not self.api_key:
            print("⚠️  GROQ_API_KEY is not set.")
            return False
        try:
            health_url = f"{self.base_url}/models"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(health_url, headers=headers, timeout=10)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Could not reach Groq API: {e}")
            return False


def get_llm_client(model: str = DEFAULT_MODEL) -> LLMClient:
    """Factory function to get LLM client."""
    return LLMClient(model=model)
