from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db.models import AppointmentRequest, Conversation, FAQ, Lead, Message
from app.db.session import get_session
from app.schemas.chat import AdminStatsResponse, AppointmentRecord, ConversationHistoryResponse, LeadRecord, MessageRecord


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/leads", response_model=list[LeadRecord])
def list_leads(session: Session = Depends(get_session)) -> list[LeadRecord]:
    leads = session.exec(select(Lead).order_by(Lead.created_at.desc())).all()
    return [
        LeadRecord(
            id=lead.id,
            name=lead.name,
            email=lead.email,
            phone=lead.phone,
            company=lead.company,
            need=lead.need,
            source=lead.source,
            created_at=lead.created_at.isoformat(),
        )
        for lead in leads
    ]


@router.get("/appointments", response_model=list[AppointmentRecord])
def list_appointments(session: Session = Depends(get_session)) -> list[AppointmentRecord]:
    appointments = session.exec(select(AppointmentRequest).order_by(AppointmentRequest.created_at.desc())).all()
    return [
        AppointmentRecord(
            id=item.id,
            lead_id=item.lead_id,
            name=item.name,
            email=item.email,
            phone=item.phone,
            company=item.company,
            need=item.need,
            preferred_date=item.preferred_date,
            preferred_time=item.preferred_time,
            notes=item.notes,
            status=item.status,
            created_at=item.created_at.isoformat(),
        )
        for item in appointments
    ]


@router.get("/stats", response_model=AdminStatsResponse)
def admin_stats(session: Session = Depends(get_session)) -> AdminStatsResponse:
    faq_count = len(session.exec(select(FAQ)).all())
    conversation_count = len(session.exec(select(Conversation)).all())
    lead_count = len(session.exec(select(Lead)).all())
    appointment_request_count = len(session.exec(select(AppointmentRequest)).all())
    return AdminStatsResponse(
        faq_count=faq_count,
        conversation_count=conversation_count,
        lead_count=lead_count,
        appointment_request_count=appointment_request_count,
    )


@router.get("/conversations/{session_id}", response_model=ConversationHistoryResponse)
def conversation_history(session_id: str, session: Session = Depends(get_session)) -> ConversationHistoryResponse:
    conversation = session.exec(select(Conversation).where(Conversation.session_id == session_id)).first()
    messages = []
    if conversation:
        messages = session.exec(select(Message).where(Message.conversation_id == conversation.id).order_by(Message.created_at)).all()
        return ConversationHistoryResponse(
            session_id=conversation.session_id,
            current_state=conversation.current_state,
            messages=[
                MessageRecord(role=message.role, content=message.content, created_at=message.created_at.isoformat())
                for message in messages
            ],
        )
    return ConversationHistoryResponse(session_id=session_id, current_state="missing", messages=[])
