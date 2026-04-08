import csv
import secrets
from io import StringIO
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import desc
from sqlmodel import Session, select

from app.core.config import get_settings
from app.db.models import AppointmentRequest, Conversation, FAQ, Lead, Message
from app.db.session import get_session
from app.schemas.chat import (
    AdminStatsResponse,
    AppointmentRecord,
    ConversationHistoryResponse,
    ConversationSummary,
    DemoSeedResponse,
    LeadRecord,
    MessageRecord,
)


router = APIRouter(prefix="/admin", tags=["admin"])
security = HTTPBasic(auto_error=False)


def require_admin(credentials: HTTPBasicCredentials | None = Depends(security)) -> None:
    settings = get_settings()
    if not settings.admin_username or not settings.admin_password:
        return
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication required",
            headers={"WWW-Authenticate": "Basic"},
        )
    username_ok = secrets.compare_digest(credentials.username, settings.admin_username)
    password_ok = secrets.compare_digest(credentials.password, settings.admin_password)
    if not (username_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
            headers={"WWW-Authenticate": "Basic"},
        )


def serialize_lead(lead: Lead) -> LeadRecord:
    assert lead.id is not None
    return LeadRecord(
        id=lead.id,
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
        company=lead.company,
        need=lead.need,
        source=lead.source,
        created_at=lead.created_at.isoformat(),
    )


def serialize_appointment(item: AppointmentRequest) -> AppointmentRecord:
    assert item.id is not None
    return AppointmentRecord(
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


@router.get("/leads", response_model=list[LeadRecord], dependencies=[Depends(require_admin)])
def list_leads(session: Session = Depends(get_session)) -> list[LeadRecord]:
    leads = session.exec(select(Lead).order_by(desc(Lead.created_at))).all()
    return [serialize_lead(lead) for lead in leads]


@router.get("/appointments", response_model=list[AppointmentRecord], dependencies=[Depends(require_admin)])
def list_appointments(session: Session = Depends(get_session)) -> list[AppointmentRecord]:
    appointments = session.exec(select(AppointmentRequest).order_by(desc(AppointmentRequest.created_at))).all()
    return [serialize_appointment(item) for item in appointments]


@router.get("/stats", response_model=AdminStatsResponse, dependencies=[Depends(require_admin)])
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


@router.get("/conversations", response_model=list[ConversationSummary], dependencies=[Depends(require_admin)])
def list_conversations(session: Session = Depends(get_session)) -> list[ConversationSummary]:
    conversations = session.exec(select(Conversation).order_by(desc(Conversation.updated_at))).all()
    result = []
    for conversation in conversations[:12]:
        assert conversation.id is not None
        message_count = len(session.exec(select(Message).where(Message.conversation_id == conversation.id)).all())
        result.append(
            ConversationSummary(
                session_id=conversation.session_id,
                current_state=conversation.current_state,
                message_count=message_count,
                updated_at=conversation.updated_at.isoformat(),
            )
        )
    return result


@router.get("/conversations/{session_id}", response_model=ConversationHistoryResponse, dependencies=[Depends(require_admin)])
def conversation_history(session_id: str, session: Session = Depends(get_session)) -> ConversationHistoryResponse:
    conversation = session.exec(select(Conversation).where(Conversation.session_id == session_id)).first()
    if conversation:
        assert conversation.id is not None
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


def build_csv_response(filename: str, rows: list[dict[str, str]]) -> Response:
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()) if rows else [])
    if rows:
        writer.writeheader()
        writer.writerows(rows)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/exports/leads.csv", dependencies=[Depends(require_admin)])
def export_leads_csv(session: Session = Depends(get_session)) -> Response:
    rows = [record.model_dump() for record in list_leads(session)]
    return build_csv_response("leads.csv", rows)


@router.get("/exports/appointments.csv", dependencies=[Depends(require_admin)])
def export_appointments_csv(session: Session = Depends(get_session)) -> Response:
    rows = [record.model_dump() for record in list_appointments(session)]
    return build_csv_response("appointments.csv", rows)


@router.post("/demo/seed", response_model=DemoSeedResponse, dependencies=[Depends(require_admin)])
def seed_demo_records(session: Session = Depends(get_session)) -> DemoSeedResponse:
    demo_leads = [
        Lead(name="Ava Brooks", email="ava@northstar-demo.test", phone="555-310-2001", company="residential", need="Interested in solar plus battery", source="demo-seed"),
        Lead(name="Noah Patel", email="noah@brightbean.test", phone="555-310-2002", company="Bright Bean Cafe", need="Commercial quote for cafe rooftop", source="demo-seed"),
    ]
    for lead in demo_leads:
        session.add(lead)
    session.commit()
    for lead in demo_leads:
        session.refresh(lead)

    demo_appointments = [
        AppointmentRequest(
            lead_id=demo_leads[0].id,
            name=demo_leads[0].name,
            email=demo_leads[0].email,
            phone=demo_leads[0].phone,
            company=demo_leads[0].company,
            need=demo_leads[0].need,
            preferred_date="Next Monday",
            preferred_time="11:00 AM",
            notes="Prefers a phone consultation first.",
            status="requested",
        ),
        AppointmentRequest(
            lead_id=demo_leads[1].id,
            name=demo_leads[1].name,
            email=demo_leads[1].email,
            phone=demo_leads[1].phone,
            company=demo_leads[1].company,
            need=demo_leads[1].need,
            preferred_date="Thursday",
            preferred_time="2:30 PM",
            notes="Would like a site visit estimate.",
            status="requested",
        ),
    ]
    for item in demo_appointments:
        session.add(item)

    conversation_count = 0
    for prompt, answer in [
        ("How much does a typical installation cost?", "Most demo residential projects start around $12,000 before incentives."),
        ("Can I request a commercial estimate?", "Yes, I can collect your company details and submit a consultation request."),
    ]:
        conversation = Conversation(session_id=str(uuid4()), current_state="detect_intent", status="seeded-demo")
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        assert conversation.id is not None
        session.add(Message(conversation_id=conversation.id, role="user", content=prompt, metadata_json="{}"))
        session.add(Message(conversation_id=conversation.id, role="assistant", content=answer, metadata_json="{}"))
        conversation_count += 1

    session.commit()
    return DemoSeedResponse(
        inserted_leads=len(demo_leads),
        inserted_appointments=len(demo_appointments),
        inserted_conversations=conversation_count,
    )
