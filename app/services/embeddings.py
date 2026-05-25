import os
from typing import List
from app.utils.logger import get_logger

logger = get_logger(__name__)

_model = None  # lazy-loaded


def _load_model():
    global _model
    if _model is not None:
        return
    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Loaded SentenceTransformer: all-MiniLM-L6-v2")
    except ImportError:
        raise RuntimeError(
            "sentence-transformers not installed. Run: pip install sentence-transformers"
        )


def generate_embedding(text: str) -> List[float]:
    """Convert a single text string into a vector."""
    _load_model()
    vector = _model.encode(text, normalize_embeddings=True)
    return vector.tolist()


def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """Convert a list of texts into vectors (efficient batch processing)."""
    _load_model()
    vectors = _model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
    return [v.tolist() for v in vectors]