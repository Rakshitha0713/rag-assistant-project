import json
from pathlib import Path
from typing import List, Dict, Any

from app.utils.logger import get_logger

logger = get_logger(__name__)


def load_documents(docs_path: str = "docs.json") -> List[Dict[str, Any]]:
    """
    Load raw documents from the JSON knowledge base file.
    Returns a list of dicts with 'title' and 'content' keys.
    """
    path = Path(docs_path)

    if not path.exists():
        logger.error(f"docs.json not found at: {path.resolve()}")
        return []

    with open(path, "r", encoding="utf-8") as f:
        documents = json.load(f)

    logger.info(f"Loaded {len(documents)} document(s) from {docs_path}")
    return documents


def save_documents(documents: List[Dict[str, Any]], docs_path: str = "docs.json") -> None:
    """
    Save documents back to the JSON file.
    Useful if documents are added or updated at runtime.
    """
    with open(docs_path, "w", encoding="utf-8") as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved {len(documents)} document(s) to {docs_path}")