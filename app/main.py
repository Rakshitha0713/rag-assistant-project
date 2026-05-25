import json
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

load_dotenv()

from app.routes.chat import router
from app.services.embeddings import generate_embeddings_batch
from app.vectorstore.store import vector_store
from app.utils.chunker import chunk_documents
from app.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(title="RAG Assistant API", version="1.0.0")

# ── Register routes ───────────────────────────────────────────────────────
app.include_router(router)

# ── Serve frontend static files ───────────────────────────────────────────
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    async def serve_frontend():
        return FileResponse(str(FRONTEND_DIR / "index.html"))


# ── Startup: index documents ─────────────────────────────────────────────
@app.on_event("startup")
async def index_documents():
    from app.services.storage import load_documents

    docs_path = Path(__file__).parent.parent / "docs.json"
    documents = load_documents(str(docs_path))

    if not documents:
        logger.error(f"No documents found in {docs_path}. Knowledge base is empty.")
        return

    logger.info(f"Loaded {len(documents)} document(s) from docs.json.")

    # Chunk
    chunks = chunk_documents(documents)
    logger.info(f"Created {len(chunks)} chunk(s) from {len(documents)} document(s).")

    # Embed (batch for efficiency)
    texts = [c["text"] for c in chunks]
    embeddings = generate_embeddings_batch(texts)
    logger.info(f"Generated {len(embeddings)} embedding(s).")

    # Attach embeddings to chunks
    for chunk, emb in zip(chunks, embeddings):
        chunk["embedding"] = emb

    # Index
    vector_store.add_chunks(chunks)
    logger.info(f"Indexing complete. Vector store size: {vector_store.size}")