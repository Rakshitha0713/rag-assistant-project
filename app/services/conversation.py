import os
from collections import defaultdict
from typing import List, Dict, Tuple

MAX_PAIRS = int(os.getenv("MAX_HISTORY_PAIRS", "5"))


class ConversationManager:
    def __init__(self, max_pairs: int = MAX_PAIRS):
        self._max_pairs = max_pairs
        # session_id -> list of (user_msg, assistant_msg) tuples
        self._sessions: Dict[str, List[Tuple[str, str]]] = defaultdict(list)

    def add_exchange(self, session_id: str, user_msg: str, assistant_msg: str) -> None:
        """Store a user-assistant exchange, trimming to max_pairs."""
        history = self._sessions[session_id]
        history.append((user_msg, assistant_msg))
        if len(history) > self._max_pairs:
            self._sessions[session_id] = history[-self._max_pairs :]

    def get_history_string(self, session_id: str) -> str:
        """
        Returns conversation history formatted as a string for the LLM prompt.
        Example:
            User: How do I reset my password?
            Assistant: You can reset it from Settings > Security.
        """
        history = self._sessions.get(session_id, [])
        if not history:
            return ""

        lines = []
        for user_msg, assistant_msg in history:
            lines.append(f"User: {user_msg}")
            lines.append(f"Assistant: {assistant_msg}")

        return "\n".join(lines)

    def clear_session(self, session_id: str) -> None:
        """Remove all history for a session."""
        self._sessions.pop(session_id, None)

    def session_count(self) -> int:
        return len(self._sessions)


# Singleton
conversation_manager = ConversationManager()