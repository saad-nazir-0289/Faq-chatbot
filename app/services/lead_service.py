from __future__ import annotations

from typing import Dict

from sqlmodel import Session

from app.db.models import Lead


def create_lead(session: Session, data: Dict[str, str]) -> Lead:
    lead = Lead(
        name=data.get("name", ""),
        email=data.get("email", ""),
        phone=data.get("phone", ""),
        company=data.get("company", ""),
        need=data.get("need", ""),
        source="chatbot",
    )
    session.add(lead)
    session.commit()
    session.refresh(lead)
    return lead
