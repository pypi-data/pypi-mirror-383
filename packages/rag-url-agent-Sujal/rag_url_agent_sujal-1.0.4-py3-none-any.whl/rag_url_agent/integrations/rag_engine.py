import numpy as np
from typing import List, Dict, Optional
import openai
from rag_url_agent.core.storage_manager import StorageManager
from rag_url_agent.utils.logger import get_logger
from rag_url_agent.utils.memory_monitor import MemoryMonitor

logger = get_logger()


class RAGEngine:
    """RAG (Retrieval-Augmented Generation) engine."""

    def __init__(self,
                 storage_manager: StorageManager,
                 embedding_model: str = "all-MiniLM-L6-v2",
                 llm_provider: str = "groq",
                 api_key: str = None,
                 model: str = "mixtral-8x7b-32768",
                 temperature: float = 0.7,
                 max_tokens: int = 2048,
                 ollama_base_url: str = "http://localhost:11434"):

        self.storage = storage_manager
        self.llm_provider = llm_provider
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.ollama_base_url = ollama_base_url

        # Initialize embedding model with error handling
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embedder = self._load_embedding_model(embedding_model)
        self.embedding_dim = self.embedder.get_sentence_embedding_dimension()

        # Initialize vector index
        self.storage.init_vector_index(self.embedding_dim)

        # Setup LLM client
        self._setup_llm_client(api_key)

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

    def _setup_llm_client(self, api_key: str):
        """Setup LLM API client."""
        if self.llm_provider == "ollama":
            from rag_url_agent.integrations.ollama_client import OllamaClient
            self.ollama_client = OllamaClient(
                base_url=self.ollama_base_url,
                model=self.model
            )
            if self.ollama_client.is_available():
                logger.info(f"Using Ollama: {self.model}")
            else:
                logger.warning("Ollama is not running!")
        elif self.llm_provider == "groq":
            openai.api_key = api_key
            openai.api_base = "https://api.groq.com/openai/v1"
            logger.info("Using Groq API")
        elif self.llm_provider == "openrouter":
            openai.api_key = api_key
            openai.api_base = "https://openrouter.ai/api/v1"
            logger.info("Using OpenRouter API")
        else:
            openai.api_key = api_key
            logger.info("Using OpenAI API")

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

    def generate_response(self, query: str, context: str, conversation_history: List[Dict] = None) -> Dict:
        """Generate response using LLM."""
        logger.info("Generating LLM response")

        messages = []
        system_prompt = """You are a helpful AI assistant that answers questions based on the provided context.
Use the context information to answer questions accurately and concisely.
If the context doesn't contain enough information to answer the question, say so clearly.
Always cite relevant information from the context when answering."""

        messages.append({"role": "system", "content": system_prompt})

        if conversation_history:
            messages.extend(conversation_history[-5:])

        user_message = f"""Context information:
{context}

Question: {query}

Please provide a detailed answer based on the context above."""

        messages.append({"role": "user", "content": user_message})

        try:
            if self.llm_provider == "ollama":
                # Use Ollama
                return self.ollama_client.chat(
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
            else:
                # Use OpenAI-compatible API
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    timeout=30
                )
                answer = response.choices[0].message.content
                return {
                    'answer': answer,
                    'model': self.model,
                    'tokens_used': response.usage.total_tokens,
                    'success': True
                }
        except Exception as e:
            logger.error(f"LLM API error: {e}")
            return {
                'answer': f"Error generating response: {str(e)}",
                'success': False,
                'error': str(e)
            }

    def query(self, question: str, k: int = 5, conversation_history: List[Dict] = None) -> Dict:
        """Main query method for RAG pipeline."""
        logger.info(f"Processing query: {question}")
        chunks = self.retrieve_relevant_chunks(question, k=k)
        if not chunks:
            return {
                'answer': "I don't have any relevant information to answer this question. Please add some URLs first.",
                'chunks': [],
                'success': False
            }
        context = self.build_context(chunks)
        response = self.generate_response(question, context, conversation_history)
        response['chunks'] = [
            {
                'text': chunk['chunk_text'][:200] + '...',
                'url_id': chunk['url_id'],
                'similarity': chunk['similarity_score']
            }
            for chunk in chunks[:3]
        ]
        return response