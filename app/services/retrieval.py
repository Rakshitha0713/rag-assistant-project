import os
from typing import List, Dict, Any, Tuple

from app.services.embeddings import generate_embedding
from app.vectorstore.store import vector_store
from app.utils.logger import get_logger

logger = get_logger(__name__)

TOP_K = int(os.getenv("TOP_K", "3"))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.30"))

FALLBACK_RESPONSE = (
    "I could not find enough information in the knowledge base to answer this question. "
    "Please rephrase your query or contact support for further assistance."
)


def retrieve(query: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Given a user query string, returns:
      (context_string, retrieved_chunks)

    context_string is either:
      - A formatted block of retrieved passages (if similarity >= threshold)
      - The FALLBACK_RESPONSE sentinel (if nothing is above threshold)

    retrieved_chunks is the raw list from the vector store (may be empty).
    """
    # Step 1 – embed the query
    query_embedding = generate_embedding(query)
    logger.info(f"Query embedding generated for: '{query[:80]}'")

    # Step 2 – similarity search
    chunks = vector_store.search(
        query_embedding=query_embedding,
        top_k=TOP_K,
        threshold=SIMILARITY_THRESHOLD,
    )

    # Step 3 – build context string
    if not chunks:
        logger.warning("No chunks passed the similarity threshold.")
        return FALLBACK_RESPONSE, []

    context_parts = []
    for chunk in chunks:
        context_parts.append(
            f"[Source: {chunk['source']} | Score: {chunk['score']:.3f}]\n{chunk['text']}"
        )

    context_string = "\n\n---\n\n".join(context_parts)
    return context_string, chunks