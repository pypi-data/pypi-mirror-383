# agent/core/chroma_storage.py

import chromadb
from chromadb.config import Settings
import numpy as np
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from agent.utils.logger import get_logger

logger = get_logger()


class ChromaStorageManager:
    """Vector storage using ChromaDB (alternative to FAISS)."""

    def __init__(self, persist_directory: str = "data/vectors"):
        self.persist_dir = Path(persist_directory)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir)
        )

        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="url_chunks",
            metadata={"hnsw:space": "cosine"}
        )

        logger.info(f"Initialized ChromaDB at {self.persist_dir}")

    def add_embeddings(self, embeddings: np.ndarray, chunk_ids: List[int],
                       metadatas: List[Dict] = None):
        """Add embeddings to ChromaDB."""
        ids = [str(chunk_id) for chunk_id in chunk_ids]
        embeddings_list = embeddings.tolist()

        if metadatas is None:
            metadatas = [{"chunk_id": cid} for cid in chunk_ids]

        self.collection.add(
            embeddings=embeddings_list,
            ids=ids,
            metadatas=metadatas
        )

        logger.info(f"Added {len(chunk_ids)} embeddings to ChromaDB")

    def search_similar(self, query_embedding: np.ndarray, k: int = 5) -> List[Tuple[int, float]]:
        """Search for similar chunks."""
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=k
        )

        if not results['ids'] or not results['ids'][0]:
            return []

        # Convert to (chunk_id, distance) tuples
        chunk_results = []
        for chunk_id, distance in zip(results['ids'][0], results['distances'][0]):
            chunk_results.append((int(chunk_id), float(distance)))

        return chunk_results

    def delete_by_ids(self, chunk_ids: List[int]):
        """Delete embeddings by chunk IDs."""
        ids = [str(cid) for cid in chunk_ids]
        self.collection.delete(ids=ids)
        logger.info(f"Deleted {len(chunk_ids)} embeddings")

    def count(self) -> int:
        """Get total number of embeddings."""
        return self.collection.count()

    def save(self):
        """Save to disk (ChromaDB auto-persists)."""
        pass