from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from backend.app.db.session import get_db
from backend.app.db.models import Profile, Conversation, Message, APIProvider, UsageLog
from backend.app.core.deps import get_current_user
from backend.app.core.security import decrypt_api_key
from backend.app.providers.registry import provider_registry

router = APIRouter(prefix="/assistant", tags=["AI Assistant"])

ASSISTANT_SYSTEM_PROMPT = """You are ExamPilot AI Assistant, an expert academic tutor and revision mentor developed by GT InnoX LLP.
Your goal is to guide students, explain difficult concepts step-by-step, clarify confusing multiple-choice options, generate relevant practice questions on demand, and provide concise revision summaries.
Be encouraging, academically precise, clear, and pedagogically sound."""

class CreateConversationRequest(BaseModel):
    title: Optional[str] = "Study Session"
    provider: Optional[str] = None
    model: Optional[str] = None

class SendMessageRequest(BaseModel):
    conversation_id: str
    content: str
    provider: Optional[str] = None
    model: Optional[str] = None

class MessageItem(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime

class ConversationItem(BaseModel):
    id: str
    title: str
    provider: Optional[str] = None
    model: Optional[str] = None
    created_at: datetime
    messages: List[MessageItem] = []

@router.get("/conversations", response_model=List[ConversationItem])
def list_conversations(
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    convs = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(desc(Conversation.created_at)).all()
    
    return [
        ConversationItem(
            id=c.id,
            title=c.title,
            provider=c.provider,
            model=c.model,
            created_at=c.created_at
        )
        for c in convs
    ]

@router.post("/conversations", response_model=ConversationItem)
def create_conversation(
    req: CreateConversationRequest,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conv = Conversation(
        user_id=current_user.id,
        title=req.title or "Study Session",
        provider=req.provider,
        model=req.model
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)

    # Add greeting message
    welcome_msg = Message(
        conversation_id=conv.id,
        role="assistant",
        content="Hello! I'm your ExamPilot 2.0 AI Tutor. Ask me any conceptual question, paste an MCQ to dissect, or ask for a quick practice quiz on any topic."
    )
    db.add(welcome_msg)
    db.commit()
    db.refresh(welcome_msg)

    return ConversationItem(
        id=conv.id,
        title=conv.title,
        provider=conv.provider,
        model=conv.model,
        created_at=conv.created_at,
        messages=[
            MessageItem(
                id=welcome_msg.id,
                role=welcome_msg.role,
                content=welcome_msg.content,
                created_at=welcome_msg.created_at
            )
        ]
    )

@router.get("/conversations/{conversation_id}", response_model=ConversationItem)
def get_conversation(
    conversation_id: str,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    msgs = db.query(Message).filter(
        Message.conversation_id == conv.id
    ).order_by(Message.created_at).all()

    return ConversationItem(
        id=conv.id,
        title=conv.title,
        provider=conv.provider,
        model=conv.model,
        created_at=conv.created_at,
        messages=[
            MessageItem(id=m.id, role=m.role, content=m.content, created_at=m.created_at)
            for m in msgs
        ]
    )

@router.post("/chat", response_model=MessageItem)
async def chat_message(
    req: SendMessageRequest,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conv = db.query(Conversation).filter(
        Conversation.id == req.conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # 1. Resolve Provider
    target_prov = req.provider or conv.provider
    saved_prov = None
    if target_prov:
        saved_prov = db.query(APIProvider).filter(
            APIProvider.user_id == current_user.id,
            APIProvider.provider == target_prov.lower().strip()
        ).first()
    if not saved_prov:
        saved_prov = db.query(APIProvider).filter(
            APIProvider.user_id == current_user.id,
            APIProvider.is_default == True
        ).first() or db.query(APIProvider).filter(
            APIProvider.user_id == current_user.id
        ).first()

    if not saved_prov:
        raise HTTPException(status_code=400, detail="No AI Provider configured. Please add an API key first.")

    provider_name = saved_prov.provider
    target_model = req.model or conv.model or saved_prov.default_model

    # Decrypt Key
    api_key = decrypt_api_key(saved_prov.encrypted_api_key)
    prov_adapter = provider_registry.get_provider(provider_name)
    if not target_model:
        models = await prov_adapter.list_models()
        target_model = models[0].id if models else "gpt-4o-mini"

    # 2. Save User Message
    user_msg = Message(
        conversation_id=conv.id,
        role="user",
        content=req.content.strip()
    )
    db.add(user_msg)
    db.commit()

    # 3. Build Conversation History
    history_msgs = db.query(Message).filter(
        Message.conversation_id == conv.id
    ).order_by(Message.created_at).all()
    formatted = [{"role": m.role, "content": m.content} for m in history_msgs[-12:]]

    # 4. Invoke Provider
    try:
        reply = await prov_adapter.chat(
            api_key=api_key,
            model=target_model,
            messages=formatted,
            system_prompt=ASSISTANT_SYSTEM_PROMPT
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Assistant generation error: {str(e)}")

    # 5. Save Assistant Message
    assistant_msg = Message(
        conversation_id=conv.id,
        role="assistant",
        content=reply["content"]
    )
    db.add(assistant_msg)

    # 6. Log Usage
    usage = UsageLog(
        user_id=current_user.id,
        provider=provider_name,
        model=target_model,
        input_tokens=reply.get("input_tokens", 0),
        output_tokens=reply.get("output_tokens", 0),
        estimated_cost=reply.get("estimated_cost", 0.0),
        feature="assistant"
    )
    db.add(usage)
    db.commit()
    db.refresh(assistant_msg)

    return MessageItem(
        id=assistant_msg.id,
        role=assistant_msg.role,
        content=assistant_msg.content,
        created_at=assistant_msg.created_at
    )

@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    current_user: Profile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(conv)
    db.commit()
    return {"message": "Conversation deleted."}

