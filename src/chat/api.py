from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth.dependencies import get_current_active_user
from ..auth.models import User
from .schemas import (
    ChatRequest, ChatResponse, SessionListResponse, SessionHistoryResponse,
    ChatSessionCreate, ChatSessionResponse
)
from .crud import (
    send_message_to_ai, get_user_sessions, get_session_by_id, 
    get_session_messages, create_chat_session, delete_session
)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/message", response_model=ChatResponse)
async def send_chat_message(
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Send a message to the AI assistant and get a response."""
    try:
        user_message, ai_message, session = send_message_to_ai(
            db=db,
            user_id=current_user.id,
            message=chat_request.message,
            session_id=chat_request.session_id
        )
        
        return ChatResponse(
            user_message=user_message,
            ai_message=ai_message,
            session=session
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message"
        )


@router.get("/sessions", response_model=SessionListResponse)
async def get_chat_sessions(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all chat sessions for the current user."""
    sessions = get_user_sessions(db, current_user.id, skip, limit)
    
    # Add message count to each session
    session_responses = []
    for session in sessions:
        session_dict = session.__dict__.copy()
        session_dict['message_count'] = len(session.messages)
        session_responses.append(ChatSessionResponse(**session_dict))
    
    return SessionListResponse(
        sessions=session_responses,
        total=len(sessions)
    )


@router.get("/sessions/{session_id}", response_model=SessionHistoryResponse)
async def get_session_history(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get the full history of a specific chat session."""
    session = get_session_by_id(db, session_id, current_user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    messages = get_session_messages(db, session_id, current_user.id)
    
    return SessionHistoryResponse(
        session=session,
        messages=messages
    )


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_new_session(
    session_data: ChatSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new chat session."""
    session = create_chat_session(db, current_user.id, session_data)
    return ChatSessionResponse(**session.__dict__, message_count=0)


@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a chat session."""
    success = delete_session(db, session_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return {"message": "Session deleted successfully"}
