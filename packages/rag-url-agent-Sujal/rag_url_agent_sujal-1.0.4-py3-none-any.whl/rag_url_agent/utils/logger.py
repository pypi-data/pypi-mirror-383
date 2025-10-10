import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


class AgentLogger:
    """Centralized logging for the RAG agent."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.logger = None

    def setup(self, name: str = "RAGAgent",
              level: str = "INFO",
              log_file: Optional[str] = None,
              max_bytes: int = 100 * 1024 * 1024,  # 100MB
              backup_count: int = 5):
        """Setup logger with file and console handlers."""

        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))

        # Clear existing handlers
        self.logger.handlers.clear()

        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        self.logger.addHandler(console_handler)

        # File handler
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            self.logger.addHandler(file_handler)

        return self.logger

    def get_logger(self) -> logging.Logger:
        """Get the logger instance."""
        if self.logger is None:
            self.setup()
        return self.logger


def get_logger() -> logging.Logger:
    """Convenience function to get logger."""
    return AgentLogger().get_logger()
# Logger Utility
