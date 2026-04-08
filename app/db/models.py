from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.utcnow()


class FAQ(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    question: str
    answer: str
    tags: str = ""
    active: bool = True


class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(index=True, unique=True)
    current_state: str = Field(default="detect_intent")
    status: str = Field(default="active")
    collected_data: str = Field(default="{}", sa_column=Column(Text, nullable=False))
    lead_id: Optional[int] = Field(default=None, foreign_key="lead.id")
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)


class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id", index=True)
    role: str
    content: str
    metadata_json: str = Field(default="{}", sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(default_factory=utcnow)


class Lead(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    phone: str
    company: str = ""
    need: str = ""
    source: str = "chatbot"
    created_at: datetime = Field(default_factory=utcnow)


class AppointmentRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    lead_id: Optional[int] = Field(default=None, foreign_key="lead.id")
    name: str
    email: str
    phone: str
    company: str = ""
    need: str = ""
    preferred_date: str
    preferred_time: str
    notes: str = ""
    status: str = "requested"
    created_at: datetime = Field(default_factory=utcnow)
