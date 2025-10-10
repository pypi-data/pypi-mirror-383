"""
LLM Router - Unified interface for all providers with fallback support.
"""

from typing import List, Dict, Optional
from rag_url_agent.integrations.llm_providers import *
from rag_url_agent.utils.logger import get_logger

logger = get_logger()


class LLMRouter:
    """
    Route LLM requests to appropriate provider.
    Supports multiple providers with automatic fallback.
    """

    PROVIDERS = {
        # Local/Offline
        'ollama': OllamaProvider,
        'vllm': VLLMProvider,
        'tgi': TGIProvider,
        'llamacpp': LlamaCppProvider,
        'lmstudio': LMStudioProvider,

        # API-based
        'groq': GroqProvider,
        'openrouter': OpenRouterProvider,
        'openai': OpenAIProvider,
        'together': TogetherAIProvider,

        # Custom
        'fastapi': FastAPIProvider,
    }

    def __init__(self, providers_config: Dict):
        """
        Initialize router with provider configurations.

        Args:
            providers_config: Dict of provider configs
            Example:
            {
                'primary': {'provider': 'ollama', 'model': 'mistral', 'base_url': '...'},
                'fallback': {'provider': 'groq', 'api_key': '...', 'model': '...'},
            }
        """
        self.providers = {}
        self.provider_order = []

        # Initialize providers
        for name, config in providers_config.items():
            try:
                provider_type = config.pop('provider')

                if provider_type not in self.PROVIDERS:
                    logger.warning(f"Unknown provider type: {provider_type}")
                    continue

                provider_class = self.PROVIDERS[provider_type]
                provider = provider_class(**config)

                self.providers[name] = {
                    'instance': provider,
                    'type': provider_type,
                    'config': config
                }
                self.provider_order.append(name)

                logger.info(f"Initialized provider '{name}' ({provider_type})")
            except Exception as e:
                logger.error(f"Failed to initialize provider '{name}': {e}")

        if not self.providers:
            raise ValueError("No providers initialized!")

    def chat(self, messages: List[Dict], temperature: float = 0.7,
             max_tokens: int = 1024, use_fallback: bool = True, **kwargs) -> Dict:
        """
        Send chat request with automatic fallback.

        Args:
            messages: Chat messages
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            use_fallback: Use fallback providers on failure
            **kwargs: Additional provider-specific params
        """
        errors = []

        for provider_name in self.provider_order:
            provider_info = self.providers[provider_name]
            provider = provider_info['instance']

            try:
                logger.info(f"Trying provider: {provider_name}")

                # Check availability
                if not provider.is_available():
                    logger.warning(f"Provider {provider_name} not available")
                    errors.append(f"{provider_name}: not available")
                    if not use_fallback:
                        break
                    continue

                # Send request
                result = provider.chat(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )

                if result['success']:
                    result['provider_used'] = provider_name
                    logger.info(f"Success with provider: {provider_name}")
                    return result
                else:
                    errors.append(f"{provider_name}: {result.get('error', 'unknown')}")
                    if not use_fallback:
                        return result

            except Exception as e:
                logger.error(f"Provider {provider_name} failed: {e}")
                errors.append(f"{provider_name}: {str(e)}")
                if not use_fallback:
                    break

        # All providers failed
        return {
            'answer': f"All providers failed. Errors: {'; '.join(errors)}",
            'success': False,
            'errors': errors
        }

    def get_available_providers(self) -> List[str]:
        """Get list of currently available providers."""
        available = []
        for name, info in self.providers.items():
            if info['instance'].is_available():
                available.append(name)
        return available

    def get_provider_info(self) -> Dict:
        """Get information about all configured providers."""
        info = {}
        for name, data in self.providers.items():
            info[name] = {
                'type': data['type'],
                'available': data['instance'].is_available(),
                'config': {k: v for k, v in data['config'].items() if k != 'api_key'}
            }
        return info

    @classmethod
    def auto_detect(cls) -> Optional['LLMRouter']:
        """Auto-detect available local providers."""
        configs = {}

        # Try Ollama
        try:
            ollama = OllamaProvider()
            if ollama.is_available():
                models = ollama.list_models()
                model = models[0] if models else 'mistral'
                configs['ollama'] = {
                    'provider': 'ollama',
                    'model': model,
                    'base_url': 'http://localhost:11434'
                }
        except:
            pass

        # Try vLLM
        try:
            vllm = VLLMProvider()
            if vllm.is_available():
                configs['vllm'] = {
                    'provider': 'vllm',
                    'base_url': 'http://localhost:8000'
                }
        except:
            pass

        # Try LM Studio
        try:
            lmstudio = LMStudioProvider()
            if lmstudio.is_available():
                configs['lmstudio'] = {
                    'provider': 'lmstudio',
                    'base_url': 'http://localhost:1234'
                }
        except:
            pass

        if configs:
            logger.info(f"Auto-detected providers: {list(configs.keys())}")
            return cls(configs)

        return None