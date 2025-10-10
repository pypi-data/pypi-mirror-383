import requests
from typing import List, Dict, Optional
from rag_url_agent.utils.logger import get_logger

logger = get_logger()


class OllamaClient:
    """Client for Ollama local LLM."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "mistral"):
        self.base_url = base_url
        self.model = model

    def chat(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 2048) -> Dict:
        """
        Send chat request to Ollama.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate

        Returns:
            Dict with response
        """
        try:
            url = f"{self.base_url}/api/chat"

            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }

            logger.info(f"Sending request to Ollama: {self.model}")

            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()

            result = response.json()

            return {
                'answer': result['message']['content'],
                'model': self.model,
                'success': True
            }

        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return {
                'answer': f"Error: {str(e)}",
                'success': False,
                'error': str(e)
            }

    def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def list_models(self) -> List[str]:
        """List available models."""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            models = response.json().get('models', [])
            return [model['name'] for model in models]
        except:
            return []