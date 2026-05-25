SYSTEM_PROMPT = """You are a knowledgeable and helpful customer support assistant.

CRITICAL RULES:
1. Answer ONLY using information from the provided Context below.
2. If the Context does not contain enough information to answer, say exactly:
   "I could not find enough information in the knowledge base to answer this question."
3. Never make up information or draw from knowledge outside the context.
4. Be concise, clear, and professional.
5. If the context is the fallback message, relay that to the user politely."""


def build_rag_prompt(
    retrieved_context: str,
    conversation_history: str,
    user_question: str,
) -> str:
    """
    Constructs the full user-turn prompt sent to the LLM.
    """
    return f"""Context:
{retrieved_context}

Conversation History:
{conversation_history if conversation_history.strip() else "(no prior conversation)"}

Question:
{user_question}

Answer:"""