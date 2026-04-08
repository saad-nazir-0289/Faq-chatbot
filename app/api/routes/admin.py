from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db.models import AppointmentRequest, Lead
from app.db.session import get_session
from app.schemas.chat import AppointmentRecord, LeadRecord


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
