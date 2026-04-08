from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db.models import Lead
from app.db.session import get_session
from app.schemas.chat import LeadRecord


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
