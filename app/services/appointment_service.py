from __future__ import annotations

from typing import Dict, Optional

from sqlmodel import Session

from app.db.models import AppointmentRequest


def create_appointment_request(session: Session, data: Dict[str, str], lead_id: Optional[int]) -> AppointmentRequest:
    appointment_request = AppointmentRequest(
        lead_id=lead_id,
        name=data.get("name", ""),
        email=data.get("email", ""),
        phone=data.get("phone", ""),
        company=data.get("company", ""),
        need=data.get("need", ""),
        preferred_date=data.get("preferred_date", ""),
        preferred_time=data.get("preferred_time", ""),
        notes=data.get("notes", ""),
    )
    session.add(appointment_request)
    session.commit()
    session.refresh(appointment_request)
    return appointment_request
