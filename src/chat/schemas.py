from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


# Chat Session Schemas
class ChatSessionBase(BaseModel):
    title: Optional[str] = None


class ChatSessionCreate(ChatSessionBase):
    pass


class ChatSessionResponse(ChatSessionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    message_count: Optional[int] = None  # For session list with message count

    class Config:
        from_attributes = True


# Chat Message Schemas
class ChatMessageBase(BaseModel):
    content: str


class ChatMessageCreate(ChatMessageBase):
    session_id: Optional[int] = None  # Optional: will create new session if not provided


class ChatMessageResponse(ChatMessageBase):
    id: int
    session_id: int
    is_user_message: bool
    created_at: datetime
    ai_model: Optional[str] = None
    processing_time: Optional[int] = None

    class Config:
        from_attributes = True


# Chat API Schemas
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[int] = None  # If not provided, creates new session


class ChatResponse(BaseModel):
    user_message: ChatMessageResponse
    ai_message: ChatMessageResponse
    session: ChatSessionResponse


class SessionListResponse(BaseModel):
    sessions: List[ChatSessionResponse]
    total: int


class SessionHistoryResponse(BaseModel):
    session: ChatSessionResponse
    messages: List[ChatMessageResponse]
