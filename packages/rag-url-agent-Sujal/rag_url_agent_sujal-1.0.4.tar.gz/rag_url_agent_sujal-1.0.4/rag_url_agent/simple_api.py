"""Simple API for RAG URL Agent - 1-2 line usage"""

from typing import Optional, Dict, List
import os
from pathlib import Path


class SimpleAgent:
    """Simplified RAG Agent for easy usage."""
    
    def __init__(
        self,
        llm: str = "ollama",
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        data_dir: str = "./rag_data",
        **kwargs
    ):
        """Initialize SimpleAgent."""
        self.llm = llm
        self.model = model or self._get_default_model(llm)
        self.api_key = api_key or self._get_api_key(llm)
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup and initialize
        self._setup_config(llm, self.model, self.api_key, str(self.data_dir), **kwargs)
        
        # Initialize full agent
        from rag_url_agent.agent import RAGAgent
        self._agent = RAGAgent()
    
    def _get_default_model(self, llm: str) -> str:
        """Get default model for provider."""
        defaults = {
            "ollama": "mistral",
            "groq": "mixtral-8x7b-32768",
            "openai": "gpt-3.5-turbo",
            "openrouter": "mistralai/mistral-7b-instruct",
            "vllm": "mistralai/Mistral-7B-Instruct-v0.2",
        }
        return defaults.get(llm, "mistral")
    
    def _get_api_key(self, llm: str) -> Optional[str]:
        """Get API key from environment."""
        env_vars = {
            "groq": "GROQ_API_KEY",
            "openai": "OPENAI_API_KEY",
            "openrouter": "OPENROUTER_API_KEY",
            "together": "TOGETHER_API_KEY",
        }
        env_var = env_vars.get(llm)
        return os.getenv(env_var, "") if env_var else None
    
    def _setup_config(self, llm: str, model: str, api_key: Optional[str], data_dir: str, **kwargs):
        """Setup minimal configuration."""
        from rag_url_agent.config import config
        
        # Build provider config
        provider_config = {"provider": llm}
        
        if llm == "ollama":
            provider_config.update({
                "model": model,
                "base_url": kwargs.get("base_url", "http://localhost:11434")
            })
        elif llm == "vllm":
            provider_config.update({
                "model": model,
                "base_url": kwargs.get("base_url", "http://localhost:8000")
            })
        elif llm in ["groq", "openai", "openrouter", "together"]:
            provider_config.update({
                "api_key": api_key or "",
                "model": model
            })
        
        # Update global config
        config.config["llm"] = {
            "providers": {"primary": provider_config},
            "use_fallback": False,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1024),
        }
        
        config.config["storage"]["database_path"] = f"{data_dir}/urls.db"
        config.config["storage"]["vector_index_path"] = f"{data_dir}/vectors"
    
    def add(self, url: str, skip_security: bool = True) -> Dict:
        """Add URL to knowledge base."""
        return self._agent.add_url(url, skip_security=skip_security)
    
    def ask(self, question: str, k: int = 5) -> str:
        """Ask a question (simple - returns just the answer)."""
        result = self._agent.query(question, k=k, use_history=True)
        return result.get("answer", "Error: Could not generate answer")
    
    def query(self, question: str, **kwargs) -> Dict:
        """Query with full metadata."""
        return self._agent.query(question, **kwargs)
    
    def list(self) -> List[Dict]:
        """List all processed URLs."""
        return self._agent.list_urls()
    
    def remove(self, url: str) -> bool:
        """Remove a URL from knowledge base."""
        return self._agent.remove_url(url)
    
    def clear_history(self):
        """Clear conversation history."""
        self._agent.clear_conversation()
    
    def stats(self) -> Dict:
        """Get statistics."""
        return self._agent.get_stats()
    
    def __call__(self, question: str) -> str:
        """Allow calling agent directly."""
        return self.ask(question)
    
    def __repr__(self) -> str:
        stats = self.stats()
        storage = stats.get("storage", {})
        return f"SimpleAgent(llm={self.llm}, urls={storage.get('num_urls', 0)})"


def quick_agent(llm: str = "ollama", **kwargs) -> SimpleAgent:
    """Quick one-liner to create agent."""
    return SimpleAgent(llm=llm, **kwargs)
