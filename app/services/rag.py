from typing import Tuple, Optional

from app.services.retrieval import retrieve, FALLBACK_RESPONSE
from app.services.llm import call_llm
from app.services.conversation import conversation_manager
from app.prompts.templates import build_rag_prompt, SYSTEM_PROMPT
from app.utils.logger import get_logger

logger = get_logger(__name__)


def run_rag(session_id: str, user_message: str) -> Tuple[str, Optional[int], int]:
    """
    Main RAG pipeline entry point.

    Returns:
        (reply: str, tokens_used: int | None, retrieved_chunks_count: int)
    """
    # ── 1. Retrieve ──────────────────────────────────────────────────────
    context_string, chunks = retrieve(user_message)
    retrieved_count = len(chunks)
    logger.info(f"Retrieved {retrieved_count} chunk(s) for session '{session_id}'.")

    # ── 2. Get conversation history ───────────────────────────────────────
    history_string = conversation_manager.get_history_string(session_id)

    # ── 3. Build prompt ───────────────────────────────────────────────────
    user_prompt = build_rag_prompt(
        retrieved_context=context_string,
        conversation_history=history_string,
        user_question=user_message,
    )

    # ── 4. Call LLM ───────────────────────────────────────────────────────
    # If context is the fallback sentinel, we still pass it to the LLM so it
    # answers politely; the LLM's system prompt enforces using only context.
    reply, tokens_used = call_llm(SYSTEM_PROMPT, user_prompt)

    # ── 5. Persist exchange ───────────────────────────────────────────────
    conversation_manager.add_exchange(session_id, user_message, reply)

    return reply, tokens_used, retrieved_count