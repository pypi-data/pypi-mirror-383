import sqlite3
import pickle
import hashlib
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from contextlib import contextmanager
from rag_url_agent.utils.logger import get_logger

logger = get_logger()

# Try FAISS first, fallback to ChromaDB
try:
    import faiss
    USE_FAISS = True
    logger.info("Using FAISS for vector storage")
except ImportError as e:
    logger.warning(f"FAISS not available: {e}")
    try:
        from rag_url_agent.core.chroma_storage import ChromaStorageManager
        USE_FAISS = False
        logger.info("Using ChromaDB for vector storage")
    except ImportError:
        raise ImportError("Neither FAISS nor ChromaDB available. Install one: pip install faiss-cpu OR pip install chromadb")


class StorageManager:
    """Manage persistent storage for URLs, content, and embeddings."""

    def __init__(self, db_path: str, vector_index_path: str):
        self.db_path = Path(db_path)
        self.vector_index_path = Path(vector_index_path)

        # Create directories
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.vector_index_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_database()

        # Initialize vector storage backend
        if USE_FAISS:
            self.index = None
            self.dimension = None
            self._index_to_chunk_id = {}
            self.backend = 'faiss'
        else:
            self.chroma_store = None
            self.backend = 'chromadb'

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def _init_database(self):
        """Initialize SQLite database schema."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # URLs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE NOT NULL,
                    final_url TEXT,
                    domain TEXT,
                    title TEXT,
                    description TEXT,
                    content_hash TEXT,
                    security_score INTEGER,
                    security_status TEXT,
                    processed_date TIMESTAMP,
                    content_type TEXT,
                    metadata TEXT
                )
            ''')

            # Chunks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url_id INTEGER,
                    chunk_index INTEGER,
                    chunk_text TEXT,
                    word_count INTEGER,
                    embedding_index INTEGER,
                    FOREIGN KEY (url_id) REFERENCES urls (id) ON DELETE CASCADE
                )
            ''')

            # Create indices
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_url ON urls(url)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_url_id ON chunks(url_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_embedding ON chunks(embedding_index)')

            logger.info("Database initialized")

    def save_url(self, url_data: Dict) -> int:
        """Save URL and metadata to database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT id FROM urls WHERE url = ?', (url_data['url'],))
            existing = cursor.fetchone()

            if existing:
                logger.info(f"URL already exists: {url_data['url']}")
                return existing[0]

            content_hash = hashlib.sha256(
                url_data.get('full_text', '').encode()
            ).hexdigest()

            cursor.execute('''
                INSERT INTO urls (
                    url, final_url, domain, title, description,
                    content_hash, security_score, security_status,
                    processed_date, content_type, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                url_data['url'],
                url_data.get('final_url'),
                url_data.get('domain'),
                url_data.get('title'),
                url_data.get('description'),
                content_hash,
                url_data.get('security_score', 0),
                url_data.get('security_status', 'unknown'),
                datetime.now(),
                url_data.get('content_type', 'html'),
                pickle.dumps(url_data.get('metadata', {}))
            ))

            url_id = cursor.lastrowid
            logger.info(f"Saved URL with id {url_id}: {url_data['url']}")
            return url_id

    def save_chunks(self, url_id: int, chunks: List[Dict]):
        """Save text chunks for a URL."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            for chunk in chunks:
                cursor.execute('''
                    INSERT INTO chunks (
                        url_id, chunk_index, chunk_text, word_count, embedding_index
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    url_id,
                    chunk['index'],
                    chunk['text'],
                    chunk['word_count'],
                    None
                ))

            logger.info(f"Saved {len(chunks)} chunks for url_id {url_id}")

    def get_url_by_id(self, url_id: int) -> Optional[Dict]:
        """Get URL data by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM urls WHERE id = ?', (url_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_url_by_url(self, url: str) -> Optional[Dict]:
        """Get URL data by URL string."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM urls WHERE url = ?', (url,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_chunks_by_url_id(self, url_id: int) -> List[Dict]:
        """Get all chunks for a URL."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM chunks WHERE url_id = ? ORDER BY chunk_index',
                (url_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def list_urls(self, limit: int = 100) -> List[Dict]:
        """List all processed URLs."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM urls ORDER BY processed_date DESC LIMIT ?',
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def delete_url(self, url: str) -> bool:
        """Delete URL and all associated data."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT id FROM urls WHERE url = ?', (url,))
            row = cursor.fetchone()

            if not row:
                logger.warning(f"URL not found for deletion: {url}")
                return False

            url_id = row[0]

            # Get chunk IDs for vector deletion
            cursor.execute('SELECT id FROM chunks WHERE url_id = ?', (url_id,))
            chunk_ids = [row[0] for row in cursor.fetchall()]

            # Delete from vector store
            if self.backend == 'chromadb' and self.chroma_store:
                self.chroma_store.delete_by_ids(chunk_ids)

            cursor.execute('DELETE FROM chunks WHERE url_id = ?', (url_id,))
            cursor.execute('DELETE FROM urls WHERE id = ?', (url_id,))

            logger.info(f"Deleted URL: {url}")
            return True

    def init_vector_index(self, dimension: int):
        """Initialize vector index."""
        if self.backend == 'faiss':
            self._init_faiss(dimension)
        else:
            self._init_chromadb()

    def _init_faiss(self, dimension: int):
        """Initialize FAISS index."""
        self.dimension = dimension
        index_file = f"{self.vector_index_path}.index"
        mapping_file = f"{self.vector_index_path}.mapping"

        if Path(index_file).exists():
            logger.info("Loading existing FAISS index")
            self.index = faiss.read_index(index_file)
            if Path(mapping_file).exists():
                with open(mapping_file, 'rb') as f:
                    self._index_to_chunk_id = pickle.load(f)
        else:
            logger.info(f"Creating new FAISS index with dimension {dimension}")
            self.index = faiss.IndexFlatL2(dimension)

    def _init_chromadb(self):
        """Initialize ChromaDB."""
        from rag_url_agent.core.chroma_storage import ChromaStorageManager
        self.chroma_store = ChromaStorageManager(str(self.vector_index_path))

    def add_embeddings(self, embeddings: np.ndarray, chunk_ids: List[int]):
        """Add embeddings to vector store."""
        if self.backend == 'chromadb':
            self.chroma_store.add_embeddings(embeddings, chunk_ids)
        else:
            self._add_faiss_embeddings(embeddings, chunk_ids)

    def _add_faiss_embeddings(self, embeddings: np.ndarray, chunk_ids: List[int]):
        """Add embeddings to FAISS."""
        if self.index is None:
            raise ValueError("Vector index not initialized")

        if embeddings.shape[1] != self.dimension:
            raise ValueError(f"Embedding dimension mismatch")

        start_idx = self.index.ntotal
        self.index.add(embeddings.astype('float32'))

        for i, chunk_id in enumerate(chunk_ids):
            faiss_idx = start_idx + i
            self._index_to_chunk_id[faiss_idx] = chunk_id

        with self._get_connection() as conn:
            cursor = conn.cursor()
            for i, chunk_id in enumerate(chunk_ids):
                faiss_idx = start_idx + i
                cursor.execute(
                    'UPDATE chunks SET embedding_index = ? WHERE id = ?',
                    (faiss_idx, chunk_id)
                )

        logger.info(f"Added {len(chunk_ids)} embeddings to FAISS")
        self.save_vector_index()

    def search_similar(self, query_embedding: np.ndarray, k: int = 5) -> List[Tuple[int, float]]:
        """Search for similar chunks."""
        if self.backend == 'chromadb':
            return self.chroma_store.search_similar(query_embedding, k)
        else:
            return self._search_faiss(query_embedding, k)

    def _search_faiss(self, query_embedding: np.ndarray, k: int = 5) -> List[Tuple[int, float]]:
        """Search FAISS index."""
        if self.index is None or self.index.ntotal == 0:
            logger.warning("FAISS index is empty")
            return []

        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)

        distances, indices = self.index.search(query_embedding.astype('float32'), k)

        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx in self._index_to_chunk_id:
                chunk_id = self._index_to_chunk_id[idx]
                results.append((chunk_id, float(distance)))

        return results

    def get_chunks_by_ids(self, chunk_ids: List[int]) -> List[Dict]:
        """Get chunk data by IDs."""
        if not chunk_ids:
            return []

        with self._get_connection() as conn:
            cursor = conn.cursor()
            placeholders = ','.join('?' * len(chunk_ids))
            cursor.execute(
                f'SELECT * FROM chunks WHERE id IN ({placeholders})',
                chunk_ids
            )
            return [dict(row) for row in cursor.fetchall()]

    def save_vector_index(self):
        """Save vector index to disk."""
        if self.backend == 'faiss' and self.index is not None:
            index_file = f"{self.vector_index_path}.index"
            mapping_file = f"{self.vector_index_path}.mapping"

            faiss.write_index(self.index, index_file)

            with open(mapping_file, 'wb') as f:
                pickle.dump(self._index_to_chunk_id, f)

            logger.info("FAISS index saved to disk")
        elif self.backend == 'chromadb':
            # ChromaDB auto-persists
            pass

    def get_stats(self) -> Dict:
        """Get database statistics."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) FROM urls')
            num_urls = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM chunks')
            num_chunks = cursor.fetchone()[0]

            cursor.execute('SELECT SUM(LENGTH(chunk_text)) FROM chunks')
            total_text_size = cursor.fetchone()[0] or 0

            num_embeddings = 0
            if self.backend == 'faiss' and self.index:
                num_embeddings = self.index.ntotal
            elif self.backend == 'chromadb' and self.chroma_store:
                num_embeddings = self.chroma_store.count()

            return {
                'num_urls': num_urls,
                'num_chunks': num_chunks,
                'total_text_size': total_text_size,
                'num_embeddings': num_embeddings,
                'db_size_mb': self.db_path.stat().st_size / 1024 / 1024 if self.db_path.exists() else 0,
                'backend': self.backend
            }