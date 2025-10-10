import numpy as np
from typing import List, Dict, Optional
import openai
from rag_url_agent.core.storage_manager import StorageManager
from rag_url_agent.utils.logger import get_logger
from rag_url_agent.utils.memory_monitor import MemoryMonitor

logger = get_logger()


class RAGEngine:
    """RAG (Retrieval-Augmented Generation) engine with multi-provider LLM support."""

    def __init__(self,
                 storage_manager: StorageManager,
                 embedding_model: str = "all-MiniLM-L6-v2",
                 llm_config: Optional[Dict] = None,
                 **kwargs):

        self.storage = storage_manager

        # Initialize embedding model
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embedder = self._load_embedding_model(embedding_model)
        self.embedding_dim = self.embedder.get_sentence_embedding_dimension()

        # Initialize vector index
        self.storage.init_vector_index(self.embedding_dim)

        # Initialize LLM Router
        self._setup_llm_router(llm_config or {})

        # Memory monitor
        self.memory_monitor = MemoryMonitor()

    def _load_embedding_model(self, model_name: str):
        """Load embedding model with fallback options."""
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Attempting to load model: {model_name}")
            model = SentenceTransformer(model_name)
            logger.info(f"Successfully loaded model: {model_name}")
            return model
        except Exception as e:
            logger.error(f"Failed to load {model_name}: {e}")
            alternative_models = [
                "paraphrase-MiniLM-L3-v2",
                "all-MiniLM-L12-v2",
                "paraphrase-albert-small-v2"
            ]
            for alt_model in alternative_models:
                try:
                    logger.info(f"Trying alternative model: {alt_model}")
                    model = SentenceTransformer(alt_model)
                    logger.info(f"Successfully loaded alternative model: {alt_model}")
                    return model
                except Exception as alt_e:
                    logger.error(f"Failed to load {alt_model}: {alt_e}")
                    continue
            raise RuntimeError("Could not load any embedding model.")

    def _setup_llm_router(self, llm_config: Dict):
        """Setup LLM router with multiple providers."""
        from rag_url_agent.integrations.llm_router import LLMRouter
        import os

        # Get providers config
        providers_config = llm_config.get('providers', {})

        if not providers_config:
            logger.warning("No providers configured in llm_config")
            # Try to load from main config
            from rag_url_agent.config import config as app_config
            llm_settings = app_config.get('llm', {})
            providers_config = llm_settings.get('providers', {})

        # Replace environment variables in config
        processed_config = {}
        for provider_name, provider_config in providers_config.items():
            processed_config[provider_name] = {}
            for key, value in provider_config.items():
                if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                    env_var = value[2:-1]
                    env_value = os.getenv(env_var, '')
                    processed_config[provider_name][key] = env_value
                else:
                    processed_config[provider_name][key] = value

        # Remove providers with missing required API keys
        valid_providers = {}
        for name, config in processed_config.items():
            # If api_key is required but empty, skip this provider
            if 'api_key' in config and config['api_key'] == '':
                logger.warning(f"Skipping provider '{name}' - missing API key")
                continue
            valid_providers[name] = config

        if not valid_providers:
            # Auto-detect local providers
            logger.warning("No providers configured, attempting auto-detect...")
            self.llm_router = LLMRouter.auto_detect()
            if not self.llm_router:
                raise ValueError("No LLM providers available! Please configure at least one provider.")
        else:
            self.llm_router = LLMRouter(valid_providers)

        # Store config
        self.temperature = llm_config.get('temperature', 0.7)
        self.max_tokens = llm_config.get('max_tokens', 1024)
        self.use_fallback = llm_config.get('use_fallback', True)

        logger.info(f"LLM Router initialized with providers: {list(self.llm_router.providers.keys())}")

    def generate_embeddings(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Generate embeddings for texts in batches."""
        logger.info(f"Generating embeddings for {len(texts)} texts")

        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.embedder.encode(
                batch,
                convert_to_numpy=True,
                show_progress_bar=False
            )
            embeddings.append(batch_embeddings)
            self.memory_monitor.check_memory()

        return np.vstack(embeddings)

    def index_chunks(self, chunks: List[Dict], url_id: int):
        """Generate and store embeddings for chunks."""
        if not chunks:
            return

        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.generate_embeddings(texts)
        stored_chunks = self.storage.get_chunks_by_url_id(url_id)
        chunk_ids = [chunk['id'] for chunk in stored_chunks]
        self.storage.add_embeddings(embeddings, chunk_ids)

        logger.info(f"Indexed {len(chunks)} chunks for url_id {url_id}")

    def retrieve_relevant_chunks(self, query: str, k: int = 5) -> List[Dict]:
        """Retrieve most relevant chunks for a query."""
        logger.info(f"Retrieving relevant chunks for query: {query[:100]}...")

        query_embedding = self.embedder.encode([query], convert_to_numpy=True)[0]
        results = self.storage.search_similar(query_embedding, k=k)

        if not results:
            logger.warning("No similar chunks found")
            return []

        chunk_ids = [chunk_id for chunk_id, _ in results]
        chunks = self.storage.get_chunks_by_ids(chunk_ids)

        score_map = {chunk_id: score for chunk_id, score in results}
        for chunk in chunks:
            chunk['similarity_score'] = score_map.get(chunk['id'], 0.0)

        chunks.sort(key=lambda x: x['similarity_score'])

        logger.info(f"Retrieved {len(chunks)} relevant chunks")
        return chunks

    def build_context(self, chunks: List[Dict], max_tokens: int = 2000) -> str:
        """Build context string from chunks with token limit."""
        context_parts = []
        total_tokens = 0

        for chunk in chunks:
            chunk_text = chunk['chunk_text']
            chunk_tokens = len(chunk_text) // 4

            if total_tokens + chunk_tokens > max_tokens:
                break

            context_parts.append(chunk_text)
            total_tokens += chunk_tokens

        return "\n\n".join(context_parts)

    def generate_response(self, query: str, context: str,
                          conversation_history: Optional[List[Dict]] = None) -> Dict:
        """Generate response using LLM router."""
        logger.info("Generating LLM response")

        # Build messages
        system_prompt = """You are a helpful AI assistant that answers questions based on the provided context.
Use the context information to answer questions accurately and concisely.
If the context doesn't contain enough information to answer the question, say so clearly.
Always cite relevant information from the context when answering."""

        messages = [{"role": "system", "content": system_prompt}]

        if conversation_history:
            # Limit history for performance
            messages.extend(conversation_history[-3:])

        # Limit context for local LLMs
        max_context = 2000
        if len(context) > max_context:
            context = context[:max_context] + "..."

        user_message = f"""Context:
{context}

Question: {query}

Answer:"""

        messages.append({"role": "user", "content": user_message})

        try:
            # Send to router
            result = self.llm_router.chat(
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                use_fallback=self.use_fallback
            )

            return result

        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return {
                'answer': f"Error generating response: {str(e)}",
                'success': False,
                'error': str(e)
            }

    def query(self, question: str, k: int = 5,
              conversation_history: Optional[List[Dict]] = None) -> Dict:
        """
        Main query method for RAG pipeline.
        Retrieves relevant context and generates answer.
        """
        logger.info(f"Processing query: {question}")

        # Retrieve relevant chunks
        chunks = self.retrieve_relevant_chunks(question, k=k)

        if not chunks:
            return {
                'answer': "I don't have any relevant information to answer this question. Please add some URLs first.",
                'chunks': [],
                'success': False
            }

        # Build context
        context = self.build_context(chunks)

        # Generate response
        response = self.generate_response(question, context, conversation_history)

        # Add retrieved chunks info
        response['chunks'] = [
            {
                'text': chunk['chunk_text'][:200] + '...',
                'url_id': chunk['url_id'],
                'similarity': chunk['similarity_score']
            }
            for chunk in chunks[:3]
        ]

        return response