import os
from typing import List, Dict, Any, Tuple

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from app.utils.logger import get_logger

logger = get_logger(__name__)

SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.30"))
TOP_K = int(os.getenv("TOP_K", "3"))


class VectorStore:
    def __init__(self):
        self._texts: List[str] = []
        self._embeddings: List[List[float]] = []
        self._metadata: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------ #
    #  Indexing                                                            #
    # ------------------------------------------------------------------ #

    def add_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        """
        Add a list of chunk records to the store.
        Each record must have keys: text, embedding, chunk_id, title, source.
        """
        for chunk in chunks:
            self._texts.append(chunk["text"])
            self._embeddings.append(chunk["embedding"])
            self._metadata.append(
                {
                    "chunk_id": chunk["chunk_id"],
                    "title": chunk["title"],
                    "source": chunk["source"],
                }
            )

        logger.info(f"VectorStore: {len(self._texts)} chunks indexed in total.")

    # ------------------------------------------------------------------ #
    #  Retrieval                                                           #
    # ------------------------------------------------------------------ #

    def search(
        self,
        query_embedding: List[float],
        top_k: int = TOP_K,
        threshold: float = SIMILARITY_THRESHOLD,
    ) -> List[Dict[str, Any]]:
        """
        Perform cosine similarity search.

        Returns a list of dicts (sorted descending by score):
          {
            "text":    str,
            "score":   float,
            "title":   str,
            "source":  str,
            "chunk_id": str,
          }

        Only results with score >= threshold are returned.
        """
        if not self._embeddings:
            logger.warning("VectorStore is empty – nothing to search.")
            return []

        query_vec = np.array(query_embedding).reshape(1, -1)
        doc_matrix = np.array(self._embeddings)

        scores: np.ndarray = cosine_similarity(query_vec, doc_matrix)[0]

        # Pair each score with its index, sort descending
        ranked: List[Tuple[float, int]] = sorted(
            enumerate(scores.tolist()), key=lambda x: x[1], reverse=True
        )

        results = []
        for idx, score in ranked[:top_k]:
            logger.info(
                f"  chunk_id={self._metadata[idx]['chunk_id']}  score={score:.4f}"
            )
            if score >= threshold:
                results.append(
                    {
                        "text": self._texts[idx],
                        "score": score,
                        "title": self._metadata[idx]["title"],
                        "source": self._metadata[idx]["source"],
                        "chunk_id": self._metadata[idx]["chunk_id"],
                    }
                )

        logger.info(f"Search returned {len(results)} chunk(s) above threshold {threshold}.")
        return results

    # ------------------------------------------------------------------ #
    #  Utility                                                             #
    # ------------------------------------------------------------------ #

    @property
    def size(self) -> int:
        return len(self._texts)


# Singleton instance used across the application
vector_store = VectorStore()