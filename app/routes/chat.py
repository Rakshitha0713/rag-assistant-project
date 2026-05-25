from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.models.schemas import ChatRequest, ChatResponse, HealthResponse, ErrorResponse
from app.services.rag import run_rag
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy")


@router.post("/api/chat", response_model=ChatResponse)
async def chat(request: Request):
    # ── Parse & validate body ─────────────────────────────────────────────
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON body."})

    try:
        chat_req = ChatRequest(**body)
    except Exception as exc:
        # Pydantic validation errors
        msgs = []
        try:
            for err in exc.errors():
                msgs.append(err.get("msg", str(err)))
        except Exception:
            msgs = [str(exc)]
        error_msg = "; ".join(msgs)
        return JSONResponse(status_code=422, content={"error": error_msg})

    # ── Run RAG pipeline ──────────────────────────────────────────────────
    try:
        reply, tokens_used, retrieved_chunks = run_rag(
            session_id=chat_req.sessionId,
            user_message=chat_req.message,
        )
    except RuntimeError as exc:
        logger.error(f"RAG pipeline error: {exc}")
        return JSONResponse(status_code=503, content={"error": str(exc)})
    except Exception as exc:
        logger.error(f"Unexpected error in /api/chat: {exc}")
        return JSONResponse(
            status_code=500, content={"error": "Internal server error."}
        )

    return ChatResponse(
        reply=reply,
        tokensUsed=tokens_used,
        retrievedChunks=retrieved_chunks,
    )