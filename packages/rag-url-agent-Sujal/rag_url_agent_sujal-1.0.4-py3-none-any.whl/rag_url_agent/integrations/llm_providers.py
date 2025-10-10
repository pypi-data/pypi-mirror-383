"""
Multi-provider LLM integration.
Supports: Ollama, vLLM, TGI, llama.cpp, Groq, OpenRouter, OpenAI, FastAPI
"""

import requests
import openai
from typing import List, Dict, Optional, Protocol
from abc import ABC, abstractmethod
from rag_url_agent.utils.logger import get_logger

logger = get_logger()


class LLMProvider(Protocol):
    """Protocol for all LLM providers."""

    def chat(self, messages: List[Dict], temperature: float = 0.7,
             max_tokens: int = 1024, **kwargs) -> Dict:
        """Send chat completion request."""
        ...

    def is_available(self) -> bool:
        """Check if provider is accessible."""
        ...


# ============================================
# LOCAL/OFFLINE PROVIDERS
# ============================================

class OllamaProvider:
    """Ollama - Local LLM runtime."""

    def __init__(self, base_url: str = "http://localhost:11434",
                 model: str = "mistral", **kwargs):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.kwargs = kwargs
        logger.info(f"Initialized Ollama: {model} at {base_url}")

    def chat(self, messages: List[Dict], temperature: float = 0.7,
             max_tokens: int = 1024, **kwargs) -> Dict:
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                        **self.kwargs
                    }
                },
                timeout=kwargs.get('timeout', 180)
            )
            response.raise_for_status()
            result = response.json()

            return {
                'answer': result['message']['content'],
                'model': self.model,
                'provider': 'ollama',
                'tokens_used': result.get('eval_count', 0),
                'success': True
            }
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return {'answer': f"Ollama Error: {str(e)}", 'success': False, 'error': str(e)}

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def list_models(self) -> List[str]:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            models = response.json().get('models', [])
            return [m['name'] for m in models]
        except:
            return []


class VLLMProvider:
    """vLLM - Fast inference server with OpenAI API compatibility."""

    def __init__(self, base_url: str = "http://localhost:8000",
                 model: str = "mistralai/Mistral-7B-Instruct-v0.2", **kwargs):
        self.base_url = base_url.rstrip('/v1').rstrip('/')
        self.model = model
        self.kwargs = kwargs
        logger.info(f"Initialized vLLM: {model} at {base_url}")

    def chat(self, messages: List[Dict], temperature: float = 0.7,
             max_tokens: int = 1024, **kwargs) -> Dict:
        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    **self.kwargs
                },
                timeout=kwargs.get('timeout', 180)
            )
            response.raise_for_status()
            result = response.json()

            return {
                'answer': result['choices'][0]['message']['content'],
                'model': self.model,
                'provider': 'vllm',
                'tokens_used': result.get('usage', {}).get('total_tokens', 0),
                'success': True
            }
        except Exception as e:
            logger.error(f"vLLM error: {e}")
            return {'answer': f"vLLM Error: {str(e)}", 'success': False, 'error': str(e)}

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=5)
            return response.status_code == 200
        except:
            return False


class TGIProvider:
    """Text Generation Inference - HuggingFace's inference server."""

    def __init__(self, base_url: str = "http://localhost:8080", **kwargs):
        self.base_url = base_url.rstrip('/')
        self.kwargs = kwargs
        logger.info(f"Initialized TGI at {base_url}")

    def chat(self, messages: List[Dict], temperature: float = 0.7,
             max_tokens: int = 1024, **kwargs) -> Dict:
        try:
            # Convert messages to prompt
            prompt = self._format_prompt(messages)

            response = requests.post(
                f"{self.base_url}/generate",
                json={
                    "inputs": prompt,
                    "parameters": {
                        "temperature": temperature,
                        "max_new_tokens": max_tokens,
                        "do_sample": True,
                        "top_p": 0.95,
                        **self.kwargs
                    }
                },
                timeout=kwargs.get('timeout', 180)
            )
            response.raise_for_status()
            result = response.json()

            return {
                'answer': result['generated_text'].strip(),
                'model': 'tgi',
                'provider': 'tgi',
                'tokens_used': result.get('details', {}).get('generated_tokens', 0),
                'success': True
            }
        except Exception as e:
            logger.error(f"TGI error: {e}")
            return {'answer': f"TGI Error: {str(e)}", 'success': False, 'error': str(e)}

    def _format_prompt(self, messages: List[Dict]) -> str:
        """Convert chat messages to prompt."""
        parts = []
        for msg in messages:
            role = msg['role']
            content = msg['content']
            if role == 'system':
                parts.append(f"<|system|>\n{content}\n")
            elif role == 'user':
                parts.append(f"<|user|>\n{content}\n")
            elif role == 'assistant':
                parts.append(f"<|assistant|>\n{content}\n")
        parts.append("<|assistant|>\n")
        return "".join(parts)

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False


class LlamaCppProvider:
    """llama.cpp - Lightweight C++ inference."""

    def __init__(self, base_url: str = "http://localhost:8080", **kwargs):
        self.base_url = base_url.rstrip('/')
        self.kwargs = kwargs
        logger.info(f"Initialized llama.cpp at {base_url}")

    def chat(self, messages: List[Dict], temperature: float = 0.7,
             max_tokens: int = 1024, **kwargs) -> Dict:
        try:
            # Convert to prompt
            prompt = self._format_prompt(messages)

            response = requests.post(
                f"{self.base_url}/completion",
                json={
                    "prompt": prompt,
                    "temperature": temperature,
                    "n_predict": max_tokens,
                    **self.kwargs
                },
                timeout=kwargs.get('timeout', 180)
            )
            response.raise_for_status()
            result = response.json()

            return {
                'answer': result['content'].strip(),
                'model': 'llamacpp',
                'provider': 'llamacpp',
                'tokens_used': result.get('tokens_evaluated', 0),
                'success': True
            }
        except Exception as e:
            logger.error(f"llama.cpp error: {e}")
            return {'answer': f"llama.cpp Error: {str(e)}", 'success': False, 'error': str(e)}

    def _format_prompt(self, messages: List[Dict]) -> str:
        parts = []
        for msg in messages:
            role = msg['role']
            content = msg['content']
            if role == 'system':
                parts.append(f"System: {content}\n")
            elif role == 'user':
                parts.append(f"User: {content}\n")
            elif role == 'assistant':
                parts.append(f"Assistant: {content}\n")
        parts.append("Assistant:")
        return "\n".join(parts)

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False


class LMStudioProvider:
    """LM Studio - Desktop app with local API."""

    def __init__(self, base_url: str = "http://localhost:1234",
                 model: str = "local-model", **kwargs):
        self.base_url = base_url.rstrip('/v1').rstrip('/')
        self.model = model
        self.kwargs = kwargs
        logger.info(f"Initialized LM Studio at {base_url}")

    def chat(self, messages: List[Dict], temperature: float = 0.7,
             max_tokens: int = 1024, **kwargs) -> Dict:
        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    **self.kwargs
                },
                timeout=kwargs.get('timeout', 180)
            )
            response.raise_for_status()
            result = response.json()

            return {
                'answer': result['choices'][0]['message']['content'],
                'model': self.model,
                'provider': 'lmstudio',
                'tokens_used': result.get('usage', {}).get('total_tokens', 0),
                'success': True
            }
        except Exception as e:
            logger.error(f"LM Studio error: {e}")
            return {'answer': f"LM Studio Error: {str(e)}", 'success': False, 'error': str(e)}

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=5)
            return response.status_code == 200
        except:
            return False


# ============================================
# API-BASED PROVIDERS
# ============================================

class GroqProvider:
    """Groq - Fast LLM inference API."""

    def __init__(self, api_key: str, model: str = "mixtral-8x7b-32768", **kwargs):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1"
        self.kwargs = kwargs
        logger.info(f"Initialized Groq: {model}")

    def chat(self, messages: List[Dict], temperature: float = 0.7,
             max_tokens: int = 1024, **kwargs) -> Dict:
        try:
            # Use OpenAI client with Groq endpoint
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **self.kwargs
            )

            return {
                'answer': response.choices[0].message.content,
                'model': self.model,
                'provider': 'groq',
                'tokens_used': response.usage.total_tokens,
                'success': True
            }
        except Exception as e:
            logger.error(f"Groq error: {e}")
            return {'answer': f"Groq Error: {str(e)}", 'success': False, 'error': str(e)}

    def is_available(self) -> bool:
        return bool(self.api_key)


class OpenRouterProvider:
    """OpenRouter - Multi-model API gateway."""

    def __init__(self, api_key: str, model: str = "mistralai/mistral-7b-instruct", **kwargs):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
        self.kwargs = kwargs
        logger.info(f"Initialized OpenRouter: {model}")

    def chat(self, messages: List[Dict], temperature: float = 0.7,
             max_tokens: int = 1024, **kwargs) -> Dict:
        try:
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **self.kwargs
            )

            return {
                'answer': response.choices[0].message.content,
                'model': self.model,
                'provider': 'openrouter',
                'tokens_used': response.usage.total_tokens,
                'success': True
            }
        except Exception as e:
            logger.error(f"OpenRouter error: {e}")
            return {'answer': f"OpenRouter Error: {str(e)}", 'success': False, 'error': str(e)}

    def is_available(self) -> bool:
        return bool(self.api_key)


class OpenAIProvider:
    """OpenAI - GPT models."""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", **kwargs):
        self.api_key = api_key
        self.model = model
        self.kwargs = kwargs
        logger.info(f"Initialized OpenAI: {model}")

    def chat(self, messages: List[Dict], temperature: float = 0.7,
             max_tokens: int = 1024, **kwargs) -> Dict:
        try:
            client = openai.OpenAI(api_key=self.api_key)

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **self.kwargs
            )

            return {
                'answer': response.choices[0].message.content,
                'model': self.model,
                'provider': 'openai',
                'tokens_used': response.usage.total_tokens,
                'success': True
            }
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return {'answer': f"OpenAI Error: {str(e)}", 'success': False, 'error': str(e)}

    def is_available(self) -> bool:
        return bool(self.api_key)


class TogetherAIProvider:
    """Together AI - Multi-model API."""

    def __init__(self, api_key: str, model: str = "mistralai/Mistral-7B-Instruct-v0.2", **kwargs):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.together.xyz/v1"
        self.kwargs = kwargs
        logger.info(f"Initialized Together AI: {model}")

    def chat(self, messages: List[Dict], temperature: float = 0.7,
             max_tokens: int = 1024, **kwargs) -> Dict:
        try:
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **self.kwargs
            )

            return {
                'answer': response.choices[0].message.content,
                'model': self.model,
                'provider': 'together',
                'tokens_used': response.usage.total_tokens,
                'success': True
            }
        except Exception as e:
            logger.error(f"Together AI error: {e}")
            return {'answer': f"Together AI Error: {str(e)}", 'success': False, 'error': str(e)}

    def is_available(self) -> bool:
        return bool(self.api_key)


# ============================================
# CUSTOM FASTAPI PROVIDER
# ============================================

class FastAPIProvider:
    """Custom FastAPI endpoint - For self-hosted models."""

    def __init__(self, base_url: str, api_key: Optional[str] = None,
                 model: str = "custom", **kwargs):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.model = model
        self.kwargs = kwargs
        logger.info(f"Initialized FastAPI provider at {base_url}")

    def chat(self, messages: List[Dict], temperature: float = 0.7,
             max_tokens: int = 1024, **kwargs) -> Dict:
        try:
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'

            # Try OpenAI-compatible endpoint first
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    **self.kwargs
                },
                headers=headers,
                timeout=kwargs.get('timeout', 180)
            )

            if response.status_code == 404:
                # Try custom endpoint
                response = requests.post(
                    f"{self.base_url}/chat",
                    json={
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        **self.kwargs
                    },
                    headers=headers,
                    timeout=kwargs.get('timeout', 180)
                )

            response.raise_for_status()
            result = response.json()

            # Handle different response formats
            if 'choices' in result:
                # OpenAI format
                answer = result['choices'][0]['message']['content']
                tokens = result.get('usage', {}).get('total_tokens', 0)
            elif 'response' in result:
                # Custom format
                answer = result['response']
                tokens = result.get('tokens', 0)
            else:
                answer = str(result)
                tokens = 0

            return {
                'answer': answer,
                'model': self.model,
                'provider': 'fastapi',
                'tokens_used': tokens,
                'success': True
            }
        except Exception as e:
            logger.error(f"FastAPI provider error: {e}")
            return {'answer': f"FastAPI Error: {str(e)}", 'success': False, 'error': str(e)}

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            try:
                response = requests.get(self.base_url, timeout=5)
                return response.status_code == 200
            except:
                return False