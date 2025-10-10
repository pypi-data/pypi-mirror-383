from typing import Dict, List, Optional
from pathlib import Path
from rag_url_agent.core import (
    URLProcessor,
    SecurityScanner,
    ContentExtractor,
    StorageManager,
    RAGEngine
)
from rag_url_agent.config import config
from rag_url_agent.utils.logger import AgentLogger, get_logger
from rag_url_agent.utils.memory_monitor import MemoryMonitor


class RAGAgent:
    """Main RAG Agent class orchestrating all components."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize RAG Agent with configuration."""

        # Setup logger
        log_config = config.get('logging')
        AgentLogger().setup(
            name="RAGAgent",
            level=log_config.get('level', 'INFO'),
            log_file=config.get_abs_path(log_config.get('file', 'logs/agent.log')),
            max_bytes=log_config.get('max_size_mb', 100) * 1024 * 1024,
            backup_count=log_config.get('backup_count', 5)
        )

        self.logger = get_logger()
        self.logger.info("=" * 50)
        self.logger.info("Initializing RAG Agent")
        self.logger.info("=" * 50)

        # Initialize memory monitor
        memory_config = config.get('memory')
        self.memory_monitor = MemoryMonitor(
            max_memory_mb=memory_config.get('max_memory_mb', 2048),
            cleanup_threshold_mb=memory_config.get('cleanup_threshold_mb', 1536)
        )

        # Initialize components
        self._init_components()

        # Conversation history
        self.conversation_history = []

        self.logger.info("RAG Agent initialized successfully")
        self.memory_monitor.log_memory_stats()

    def _init_components(self):
        """Initialize all agent components."""

        # URL Processor
        self.logger.info("Initializing URL Processor")
        security_config = config.get('security')
        self.url_processor = URLProcessor(
            max_redirects=security_config.get('max_redirects', 5),
            timeout=10
        )

        # Security Scanner
        self.logger.info("Initializing Security Scanner")
        self.security_scanner = SecurityScanner(
            virustotal_api_key=security_config.get('virustotal_api_key'),
            google_safe_browsing_api_key=security_config.get('google_safe_browsing_api_key'),
            cache_duration_hours=security_config.get('cache_duration_hours', 24)
        )

        # Content Extractor
        self.logger.info("Initializing Content Extractor")
        processing_config = config.get('processing')
        self.content_extractor = ContentExtractor(
            max_content_size=processing_config.get('max_content_size', 10 * 1024 * 1024),
            timeout=30,
            chunk_size=processing_config.get('chunk_size', 500),
            chunk_overlap=processing_config.get('chunk_overlap', 50)
        )

        # Storage Manager
        self.logger.info("Initializing Storage Manager")
        storage_config = config.get('storage')
        db_path = config.get_abs_path(storage_config.get('database_path', 'data/urls.db'))
        vector_path = config.get_abs_path(storage_config.get('vector_index_path', 'data/vectors/faiss_index'))

        self.storage = StorageManager(
            db_path=str(db_path),
            vector_index_path=str(vector_path)
        )

        # RAG Engine with multi-provider support
        self.logger.info("Initializing RAG Engine")
        llm_config = config.get('llm')
        embeddings_config = config.get('embeddings')

        self.rag_engine = RAGEngine(
            storage_manager=self.storage,
            embedding_model=embeddings_config.get('model', 'all-MiniLM-L6-v2'),
            llm_config=llm_config
        )

    def add_url(self, url: str, skip_security: bool = False) -> Dict:
        """Add and process a URL."""
        self.logger.info(f"Adding URL: {url}")

        try:
            # Step 1: Process URL
            self.logger.info("Step 1: Processing URL")
            url_info = self.url_processor.process_url(url)

            if not url_info:
                return {'success': False, 'error': 'Invalid URL or failed to process', 'url': url}

            final_url = url_info['final']
            domain = url_info['domain']

            # Check if already processed
            existing = self.storage.get_url_by_url(final_url)
            if existing:
                self.logger.info(f"URL already processed: {final_url}")
                return {
                    'success': True,
                    'message': 'URL already exists in database',
                    'url': final_url,
                    'url_id': existing['id'],
                    'already_exists': True
                }

            # Step 2: Security Scan
            if not skip_security:
                self.logger.info("Step 2: Security scanning")
                security_result = self.security_scanner.scan_url(final_url, domain)

                if not security_result['is_safe']:
                    self.logger.warning(f"URL failed security check: {security_result}")
                    return {
                        'success': False,
                        'error': 'URL failed security check',
                        'security_result': security_result,
                        'url': final_url
                    }
            else:
                security_result = {'is_safe': True, 'score': 0, 'methods': ['skipped']}

            # Step 3: Extract Content
            self.logger.info("Step 3: Extracting content")
            content = self.content_extractor.extract_content(final_url)

            if not content:
                return {'success': False, 'error': 'Failed to extract content from URL', 'url': final_url}

            # Step 4: Save to Storage
            self.logger.info("Step 4: Saving to storage")
            url_data = {
                'url': final_url,
                'final_url': final_url,
                'domain': domain,
                'title': content['title'],
                'description': content['description'],
                'full_text': content['full_text'],
                'security_score': security_result['score'],
                'security_status': 'safe' if security_result['is_safe'] else 'unsafe',
                'content_type': content['content_type'],
                'metadata': content['metadata']
            }

            url_id = self.storage.save_url(url_data)
            self.storage.save_chunks(url_id, content['chunks'])

            # Step 5: Generate and Index Embeddings
            self.logger.info("Step 5: Generating embeddings")
            self.rag_engine.index_chunks(content['chunks'], url_id)

            # Check memory
            self.memory_monitor.check_memory()

            self.logger.info(f"Successfully processed URL: {final_url}")

            return {
                'success': True,
                'url': final_url,
                'url_id': url_id,
                'title': content['title'],
                'num_chunks': len(content['chunks']),
                'security_score': security_result['score'],
                'already_exists': False
            }

        except Exception as e:
            self.logger.error(f"Error adding URL {url}: {e}", exc_info=True)
            return {'success': False, 'error': str(e), 'url': url}

    def query(self, question: str, k: int = 5, use_history: bool = True) -> Dict:
        """Query the knowledge base."""
        self.logger.info(f"Query: {question}")

        try:
            history = self.conversation_history if use_history else None
            result = self.rag_engine.query(question, k=k, conversation_history=history)

            if use_history and result.get('success'):
                self.conversation_history.append({'role': 'user', 'content': question})
                self.conversation_history.append({'role': 'assistant', 'content': result['answer']})

                if len(self.conversation_history) > 10:
                    self.conversation_history = self.conversation_history[-10:]

            return result

        except Exception as e:
            self.logger.error(f"Error querying: {e}", exc_info=True)
            return {'success': False, 'error': str(e), 'answer': f"An error occurred: {str(e)}"}

    def list_urls(self, limit: int = 100) -> List[Dict]:
        """List all processed URLs."""
        try:
            return self.storage.list_urls(limit=limit)
        except Exception as e:
            self.logger.error(f"Error listing URLs: {e}")
            return []

    def remove_url(self, url: str) -> bool:
        """Remove a URL and all associated data."""
        self.logger.info(f"Removing URL: {url}")

        try:
            url_info = self.url_processor.process_url(url)
            if url_info:
                url = url_info['final']

            success = self.storage.delete_url(url)

            if success:
                self.logger.info(f"Successfully removed URL: {url}")
            else:
                self.logger.warning(f"URL not found: {url}")

            return success

        except Exception as e:
            self.logger.error(f"Error removing URL {url}: {e}")
            return False

    def security_check(self, url: str) -> Dict:
        """Perform security check on URL without adding it."""
        self.logger.info(f"Security check for: {url}")

        try:
            url_info = self.url_processor.process_url(url)

            if not url_info:
                return {'success': False, 'error': 'Invalid URL'}

            final_url = url_info['final']
            domain = url_info['domain']

            security_result = self.security_scanner.scan_url(final_url, domain)

            return {
                'success': True,
                'url': final_url,
                'domain': domain,
                'security_result': security_result
            }

        except Exception as e:
            self.logger.error(f"Error in security check: {e}")
            return {'success': False, 'error': str(e)}

    def get_stats(self) -> Dict:
        """Get agent statistics."""
        try:
            storage_stats = self.storage.get_stats()
            memory_stats = self.memory_monitor.get_memory_usage()

            return {
                'storage': storage_stats,
                'memory': memory_stats,
                'conversation_length': len(self.conversation_history)
            }
        except Exception as e:
            self.logger.error(f"Error getting stats: {e}")
            return {}

    def clear_conversation(self):
        """Clear conversation history."""
        self.conversation_history.clear()
        self.logger.info("Conversation history cleared")

    def cleanup(self):
        """Cleanup resources."""
        self.logger.info("Cleaning up resources")
        self.memory_monitor.cleanup()
        self.storage.save_vector_index()
