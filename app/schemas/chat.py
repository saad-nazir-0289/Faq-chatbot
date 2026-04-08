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


class LeadRecord(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    company: str
    need: str
    source: str
    created_at: str


class AppointmentRecord(BaseModel):
    id: int
    lead_id: Optional[int] = None
    name: str
    email: str
    phone: str
    company: str
    need: str
    preferred_date: str
    preferred_time: str
    notes: str
    status: str
    created_at: str


class AdminStatsResponse(BaseModel):
    faq_count: int
    conversation_count: int
    lead_count: int
    appointment_request_count: int


class MessageRecord(BaseModel):
    role: str
    content: str
    created_at: str


class ConversationHistoryResponse(BaseModel):
    session_id: str
    current_state: str
    messages: List[MessageRecord] = Field(default_factory=list)


class ConversationSummary(BaseModel):
    session_id: str
    current_state: str
    message_count: int
    updated_at: str


class DemoSeedResponse(BaseModel):
    inserted_leads: int
    inserted_appointments: int
    inserted_conversations: int
