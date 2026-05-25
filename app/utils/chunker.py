from typing import List, Dict, Any


CHUNK_SIZE_CHARS = 1200   # ≈ 300 tokens  (1 token ≈ 4 chars)
OVERLAP_CHARS = 200       # overlap keeps context between chunks


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE_CHARS, overlap: int = OVERLAP_CHARS) -> List[str]:
    """
    Splits text into overlapping chunks.
    Returns a list of chunk strings.
    """
    chunks: List[str] = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = end - overlap  # move back by overlap for continuity

    return chunks


def chunk_documents(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Takes a list of raw documents (title + content) and returns a flat list
    of chunk records, each containing:
      - chunk_id   : "title_0", "title_1", …
      - title      : original document title
      - text       : the chunk text
      - source     : same as title (required metadata)
    """
    all_chunks: List[Dict[str, Any]] = []

    for doc in documents:
        title = doc.get("title", "Untitled")
        content = doc.get("content", "")
        pieces = chunk_text(content)

        for idx, piece in enumerate(pieces):
            all_chunks.append(
                {
                    "chunk_id": f"{title}__{idx}",
                    "title": title,
                    "text": piece,
                    "source": title,
                }
            )

    return all_chunks