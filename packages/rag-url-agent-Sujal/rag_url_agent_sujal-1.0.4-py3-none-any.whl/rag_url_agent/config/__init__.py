import json
import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv


class Config:
    """Configuration manager for the RAG agent."""

    def __init__(self, config_path: str = None):
        # Get the correct base directory
        self.base_dir = Path(__file__).parent.parent.parent  # Go up to project root
        
        if config_path is None:
            # Look for settings.json in the config directory of the package
            config_path = Path(__file__).parent / "settings.json"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._load_env_vars()
        self._create_directories()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # If config file not found, return default config
            print(f"Warning: Config file not found at {self.config_path}, using defaults")
            return self._get_default_config()
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")

    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "llm": {
                "providers": {
                    "primary": {
                        "provider": "ollama",
                        "model": "mistral",
                        "base_url": "http://localhost:11434"
                    }
                },
                "use_fallback": False,
                "temperature": 0.7,
                "max_tokens": 1024
            },
            "embeddings": {
                "model": "all-MiniLM-L6-v2",
                "batch_size": 16,
                "max_length": 512
            },
            "processing": {
                "chunk_size": 500,
                "chunk_overlap": 50,
                "max_content_size": 10485760,
                "max_chunks_per_url": 1000
            },
            "security": {
                "virustotal_api_key": "",
                "google_safe_browsing_api_key": "",
                "enable_virustotal": False,
                "enable_safe_browsing": False,
                "cache_duration_hours": 24,
                "max_redirects": 5
            },
            "storage": {
                "database_path": "data/urls.db",
                "vector_index_path": "data/vectors/faiss_index",
                "backup_enabled": True,
                "max_db_size_mb": 1000
            },
            "memory": {
                "max_memory_mb": 2048,
                "cleanup_threshold_mb": 1536,
                "enable_monitoring": True
            },
            "logging": {
                "level": "INFO",
                "file": "logs/agent.log",
                "max_size_mb": 100,
                "backup_count": 5
            }
        }

    def _load_env_vars(self):
        """Load environment variables and override config."""
        load_dotenv()

        # Override API keys from environment
        env_mappings = {
            'GROQ_API_KEY': ['llm', 'groq_api_key'],
            'OPENROUTER_API_KEY': ['llm', 'openrouter_api_key'],
            'VIRUSTOTAL_API_KEY': ['security', 'virustotal_api_key'],
            'GOOGLE_SAFE_BROWSING_API_KEY': ['security', 'google_safe_browsing_api_key']
        }

        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                self._set_nested(self.config, config_path, value)

    def _set_nested(self, d: dict, path: list, value: Any):
        """Set nested dictionary value."""
        for key in path[:-1]:
            d = d.setdefault(key, {})
        d[path[-1]] = value

    def _create_directories(self):
        """Create necessary directories."""
        directories = [
            self.base_dir / "data",
            self.base_dir / "data" / "vectors",
            self.base_dir / "logs"
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def get(self, *keys, default=None):
        """Get configuration value using dot notation."""
        value = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
            if value is None:
                return default
        return value

    def set(self, *keys, value):
        """Set configuration value using dot notation."""
        d = self.config
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value

    def save(self):
        """Save configuration to file."""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def get_abs_path(self, relative_path: str) -> Path:
        """Convert relative path to absolute path."""
        return self.base_dir / relative_path


# Global config instance
config = Config()
