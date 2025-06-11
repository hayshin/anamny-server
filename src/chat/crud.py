import time
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from agno.agent import Agent
from agno.models.google import Gemini
from agno.memory.v2 import Memory

from .models import ChatSession, ChatMessage
from .schemas import ChatSessionCreate, ChatMessageCreate
from ..config import settings

# Initialize the AI agent
def get_agent():
    """Get configured AI agent instance."""
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not configured")
    
    return Agent(
        model=Gemini(id="gemini-1.5-flash", api_key=settings.gemini_api_key),
        memory=Memory(),  # Multi-user support requires Memory.v2
        add_history_to_messages=True,
        instructions="""
You are an AI doctor who helps detect and prevent diseases. 
Based on the patient's symptoms and other diseases, tell him what's wrong with him. 
Recommend the necessary tests and which doctor he needs to visit in reality. 
If you don't have enough data, ask the patient for it.

Important: Always remind users that you are providing general information only and 
that they should consult with a healthcare professional for proper diagnosis and treatment.
"""
    )


def create_chat_session(db: Session, user_id: int, session_data: ChatSessionCreate) -> ChatSession:
    """Create a new chat session for a user."""
    db_session = ChatSession(
        user_id=user_id,
        title=session_data.title
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def get_user_sessions(db: Session, user_id: int, skip: int = 0, limit: int = 20) -> List[ChatSession]:
    """Get all chat sessions for a user."""
    return db.query(ChatSession).filter(
        ChatSession.user_id == user_id,
        ChatSession.is_active == True
    ).order_by(desc(ChatSession.updated_at)).offset(skip).limit(limit).all()


def get_session_by_id(db: Session, session_id: int, user_id: int) -> Optional[ChatSession]:
    """Get a specific session by ID for a user."""
    return db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == user_id,
        ChatSession.is_active == True
    ).first()


def get_session_messages(db: Session, session_id: int, user_id: int) -> List[ChatMessage]:
    """Get all messages in a session."""
    session = get_session_by_id(db, session_id, user_id)
    if not session:
        return []
    
    return db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).all()


def create_message(db: Session, session_id: int, content: str, is_user_message: bool, 
                  ai_model: Optional[str] = None, processing_time: Optional[int] = None) -> ChatMessage:
    """Create a new message in a session."""
    db_message = ChatMessage(
        session_id=session_id,
        content=content,
        is_user_message=is_user_message,
        ai_model=ai_model,
        processing_time=processing_time
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def send_message_to_ai(db: Session, user_id: int, message: str, session_id: Optional[int] = None) -> tuple[ChatMessage, ChatMessage, ChatSession]:
    """
    Send a message to the AI and get response.
    Returns (user_message, ai_message, session).
    """
    # Validate message
    if not message or not message.strip():
        raise ValueError("Message cannot be empty")
    
    # Create or get session
    if session_id:
        session = get_session_by_id(db, session_id, user_id)
        if not session:
            raise ValueError("Session not found")
    else:
        # Create new session with a title based on the first message
        title = message[:50] + "..." if len(message) > 50 else message
        session = create_chat_session(db, user_id, ChatSessionCreate(title=title))
    
    # Create user message
    user_message = create_message(db, session.id, message, True)
    
    # Get AI response
    start_time = time.time()
    try:
        # Get agent instance
        agent = get_agent()
        
        response = agent.run(
            message=message.strip(),
            user_id=str(user_id),
            session_id=f"session_{session.id}",
        )
        ai_response_text = response.content if hasattr(response, 'content') else str(response)
        processing_time = int((time.time() - start_time) * 1000)  # milliseconds
        
        # Create AI message
        ai_message = create_message(
            db, session.id, ai_response_text, False, 
            ai_model="gemini-1.5-flash", processing_time=processing_time
        )
        
        # Update session timestamp
        session.updated_at = db.query(ChatMessage).filter(
            ChatMessage.id == ai_message.id
        ).first().created_at
        db.commit()
        
        return user_message, ai_message, session
        
    except Exception as e:
        # Create error message
        print(f"AI Error: {e}")
        error_message = f"I apologize, but I'm experiencing technical difficulties right now. Please try again in a moment."
        processing_time = int((time.time() - start_time) * 1000)
        
        ai_message = create_message(
            db, session.id, error_message, False,
            ai_model="error", processing_time=processing_time
        )
        
        return user_message, ai_message, session


def delete_session(db: Session, session_id: int, user_id: int) -> bool:
    """Soft delete a chat session."""
    session = get_session_by_id(db, session_id, user_id)
    if not session:
        return False
    
    session.is_active = False
    db.commit()
    return True
