import psutil
import gc
from typing import Dict, Optional
from rag_url_agent.utils.logger import get_logger

logger = get_logger()


class MemoryMonitor:
    """Monitor and manage memory usage."""

    def __init__(self, max_memory_mb: int = 2048, cleanup_threshold_mb: int = 1536):
        self.max_memory_mb = max_memory_mb
        self.cleanup_threshold_mb = cleanup_threshold_mb
        self.process = psutil.Process()

    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics."""
        memory_info = self.process.memory_info()
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
            'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
            'percent': self.process.memory_percent()
        }

    def check_memory(self) -> bool:
        """Check if memory usage is within limits."""
        usage = self.get_memory_usage()

        if usage['rss_mb'] > self.max_memory_mb:
            logger.warning(f"Memory usage ({usage['rss_mb']:.2f} MB) exceeds maximum ({self.max_memory_mb} MB)")
            return False

        if usage['rss_mb'] > self.cleanup_threshold_mb:
            logger.info(f"Memory usage ({usage['rss_mb']:.2f} MB) exceeds cleanup threshold")
            self.cleanup()

        return True

    def cleanup(self):
        """Force garbage collection to free memory."""
        logger.info("Running garbage collection...")
        before = self.get_memory_usage()['rss_mb']

        gc.collect()

        after = self.get_memory_usage()['rss_mb']
        freed = before - after
        logger.info(f"Freed {freed:.2f} MB of memory")

    def log_memory_stats(self):
        """Log current memory statistics."""
        stats = self.get_memory_usage()
        logger.info(f"Memory: RSS={stats['rss_mb']:.2f}MB, VMS={stats['vms_mb']:.2f}MB, {stats['percent']:.1f}%")
# Memory Monitor
