from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ChatStartResponse(BaseModel):
    session_id: str
    state: str
    message: str
    quick_replies: List[str] = Field(default_factory=list)


class ChatMessageRequest(BaseModel):
    session_id: str
    message: str


class ChatMessageResponse(BaseModel):
    session_id: str
    state: str
    message: str
    quick_replies: List[str] = Field(default_factory=list)
    collected_data: Dict[str, Any] = Field(default_factory=dict)
    needs_handoff: bool = False
    lead_submitted: bool = False
    appointment_requested: bool = False


class HealthResponse(BaseModel):
    status: str
    app_name: str


class FlowResult(BaseModel):
    state: str
    message: str
    quick_replies: List[str] = Field(default_factory=list)
    collected_data: Dict[str, Any]
    needs_handoff: bool = False
    lead_submitted: bool = False
    appointment_requested: bool = False
    lead_record: Optional[Dict[str, Any]] = None
    appointment_record: Optional[Dict[str, Any]] = None
