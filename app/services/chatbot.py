from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlmodel import Session, select

from app.db.models import Conversation, Message
from app.schemas.chat import ChatMessageResponse, ChatStartResponse
from app.services.flow_engine import process_message
from app.services.helpers import dumps_json, loads_json


WELCOME_MESSAGE = (
    "Hi, welcome to Northstar Solar. I can answer common questions about installs, pricing, and service plans, collect your details, or help you request a consultation."
)


def create_conversation(session: Session) -> ChatStartResponse:
    session_id = str(uuid4())
    conversation = Conversation(session_id=session_id, current_state="detect_intent")
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    assert conversation.id is not None
    conversation_id = conversation.id

    bot_message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=WELCOME_MESSAGE,
        metadata_json=dumps_json(
            {"quick_replies": ["See pricing", "Request a consultation", "Ask about install time"]}
        ),
    )
    session.add(bot_message)
    session.commit()

    return ChatStartResponse(
        session_id=session_id,
        state=conversation.current_state,
        message=WELCOME_MESSAGE,
        quick_replies=["See pricing", "Request a consultation", "Ask about install time"],
    )


async def handle_message(session: Session, session_id: str, user_message: str) -> ChatMessageResponse:
    conversation = session.exec(select(Conversation).where(Conversation.session_id == session_id)).first()
    if not conversation:
        raise ValueError("Conversation not found")
    assert conversation.id is not None
    conversation_id = conversation.id

    session.add(
        Message(
            conversation_id=conversation_id,
            role="user",
            content=user_message,
            metadata_json="{}",
        )
    )
    session.commit()

    collected_data = loads_json(conversation.collected_data)
    result = await process_message(session, conversation, user_message, collected_data)

    conversation.current_state = result.state
    conversation.collected_data = dumps_json(result.collected_data)
    conversation.updated_at = datetime.now(UTC)
    session.add(conversation)
    session.commit()

    session.add(
        Message(
            conversation_id=conversation_id,
            role="assistant",
            content=result.message,
            metadata_json=dumps_json({"quick_replies": result.quick_replies}),
        )
    )
    session.commit()

    return ChatMessageResponse(
        session_id=session_id,
        state=result.state,
        message=result.message,
        quick_replies=result.quick_replies,
        collected_data=result.collected_data,
        needs_handoff=result.needs_handoff,
        lead_submitted=result.lead_submitted,
        appointment_requested=result.appointment_requested,
    )
