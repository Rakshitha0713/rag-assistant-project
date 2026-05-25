from pydantic import BaseModel, field_validator
from typing import Optional


class ChatRequest(BaseModel):
    sessionId: str
    message: str

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Message field is required and cannot be empty")
        return v.strip()

    @field_validator("sessionId")
    @classmethod
    def session_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("sessionId field is required")
        return v.strip()


class ChatResponse(BaseModel):
    reply: str
    tokensUsed: Optional[int] = None
    retrievedChunks: int = 0


class HealthResponse(BaseModel):
    status: str


class ErrorResponse(BaseModel):
    error: str