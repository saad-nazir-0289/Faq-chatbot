from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.models import FAQ
from app.db.session import get_session
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse, ChatStartResponse
from app.services.chatbot import create_conversation, handle_message
from app.services.faq_service import get_all_faqs


router = APIRouter(tags=["chat"])


@router.post("/chat/start", response_model=ChatStartResponse)
def start_chat(session: Session = Depends(get_session)) -> ChatStartResponse:
    return create_conversation(session)


@router.post("/chat/message", response_model=ChatMessageResponse)
async def post_message(payload: ChatMessageRequest, session: Session = Depends(get_session)) -> ChatMessageResponse:
    try:
        return await handle_message(session, payload.session_id, payload.message)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/faqs", response_model=list[FAQ])
def list_faqs(session: Session = Depends(get_session)) -> list[FAQ]:
    return get_all_faqs(session)
