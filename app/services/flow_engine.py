from __future__ import annotations

from typing import Dict, List

from sqlmodel import Session

from app.schemas.chat import FlowResult
from app.services.ai_service import ai_service
from app.services.appointment_service import create_appointment_request
from app.services.faq_service import search_faqs
from app.services.helpers import (
    extract_email,
    extract_phone,
    looks_like_no,
    looks_like_yes,
    normalize_text,
    validate_email,
    validate_phone,
)
from app.services.lead_service import create_lead


FIELD_ORDER = ["name", "email", "phone", "company", "need"]


def detect_intent(message: str) -> str:
    lowered = message.lower()
    appointment_terms = ["appointment", "book", "call", "demo", "meeting", "schedule", "consultation", "site visit"]
    lead_terms = ["quote", "pricing", "contact", "sales", "interested", "trial", "help", "estimate"]
    faq_terms = ["hours", "support", "service", "how", "what", "where", "when", "faq", "install", "battery", "solar"]
    if any(term in lowered for term in appointment_terms):
        return "appointment"
    if any(term in lowered for term in lead_terms):
        return "lead"
    if "?" in lowered or any(term in lowered for term in faq_terms):
        return "faq"
    return "lead"


def next_missing_field(data: Dict[str, str]) -> str | None:
    for field in FIELD_ORDER:
        if not data.get(field):
            return field
    return None


def question_for_field(field: str) -> str:
    prompts = {
        "name": "To get started, what is your name?",
        "email": "What email should Northstar Solar use to follow up?",
        "phone": "What phone number is best in case our energy consultant needs to reach you quickly?",
        "company": "What company are you with? If this is for your home, just say residential.",
        "need": "What do you need help with? For example, rooftop solar, battery backup, or a pricing estimate.",
    }
    return prompts[field]


def date_prompt() -> str:
    return "What date works best for your consultation request?"


def time_prompt() -> str:
    return "What time do you prefer on that date for a call or site visit?"


def notes_prompt() -> str:
    return "Any extra notes for the Northstar Solar team before we submit your request? You can also say 'none'."


async def process_message(session: Session, conversation, message: str, data: Dict[str, str]) -> FlowResult:
    clean_message = normalize_text(message)
    state = conversation.current_state

    if state == "detect_intent":
        intent = detect_intent(clean_message)
        if intent == "faq":
            faqs = search_faqs(session, clean_message)
            if faqs:
                fallback = f"Here is what I found for Northstar Solar: {faqs[0].answer} If you want, I can also collect your details or help you request a consultation."
                answer = await ai_service.draft_faq_answer(clean_message, faqs, fallback)
                return FlowResult(
                    state="detect_intent",
                    message=answer,
                    quick_replies=["Request a consultation", "Leave my details", "Ask another question"],
                    collected_data=data,
                )

            fallback = f"I do not have a precise answer for that yet, but I can help you reach the Northstar Solar team. {question_for_field('name')}"
            answer = await ai_service.polish_message(fallback, "faq_fallback")
            return FlowResult(
                state="collect_name",
                message=answer,
                quick_replies=["Leave my details", "Request a consultation"],
                collected_data=data,
            )

        if intent in {"lead", "appointment"}:
            data["wants_appointment"] = "yes" if intent == "appointment" else data.get("wants_appointment", "")
            fallback = question_for_field("name")
            answer = await ai_service.polish_message(fallback, "collect_name")
            return FlowResult(
                state="collect_name",
                message=answer,
                quick_replies=[],
                collected_data=data,
            )

    if state == "collect_name":
        if len(clean_message) < 2:
            return FlowResult(
                state="collect_name",
                message="Please share your name so I can save your request correctly.",
                quick_replies=[],
                collected_data=data,
            )
        data["name"] = clean_message
        fallback = question_for_field("email")
        answer = await ai_service.polish_message(fallback, "collect_email")
        return FlowResult(state="collect_email", message=answer, quick_replies=[], collected_data=data)

    if state == "collect_email":
        email = extract_email(clean_message)
        if not email or not validate_email(email):
            return FlowResult(
                state="collect_email",
                message="That email looks incomplete. Please share a valid email address so we can follow up.",
                quick_replies=[],
                collected_data=data,
            )
        data["email"] = email
        fallback = question_for_field("phone")
        answer = await ai_service.polish_message(fallback, "collect_phone")
        return FlowResult(state="collect_phone", message=answer, quick_replies=[], collected_data=data)

    if state == "collect_phone":
        phone = extract_phone(clean_message)
        if not phone or not validate_phone(phone):
            return FlowResult(
                state="collect_phone",
                message="Please share a valid phone number with at least 7 digits.",
                quick_replies=[],
                collected_data=data,
            )
        data["phone"] = phone
        fallback = question_for_field("company")
        answer = await ai_service.polish_message(fallback, "collect_company")
        return FlowResult(state="collect_company", message=answer, quick_replies=[], collected_data=data)

    if state == "collect_company":
        data["company"] = clean_message if clean_message.lower() not in {"none", "n/a"} else "Individual"
        fallback = question_for_field("need")
        answer = await ai_service.polish_message(fallback, "collect_need")
        return FlowResult(state="collect_need", message=answer, quick_replies=[], collected_data=data)

    if state == "collect_need":
        data["need"] = clean_message
        fallback = "Would you like to request a consultation with the team as well?"
        answer = await ai_service.polish_message(fallback, "ask_appointment_request")
        return FlowResult(
            state="ask_appointment_request",
            message=answer,
            quick_replies=["Yes, request a consultation", "No, just send my details"],
            collected_data=data,
        )

    if state == "ask_appointment_request":
        if looks_like_yes(clean_message) or "book" in clean_message.lower() or "call" in clean_message.lower():
            data["wants_appointment"] = "yes"
            return FlowResult(state="collect_preferred_date", message=date_prompt(), quick_replies=[], collected_data=data)
        if looks_like_no(clean_message):
            lead = create_lead(session, data)
            fallback = "Thanks, your details are in. A Northstar Solar specialist will review your request and follow up soon."
            answer = await ai_service.polish_message(fallback, "confirm_lead")
            return FlowResult(
                state="detect_intent",
                message=answer,
                quick_replies=["Ask a question", "Request a consultation"],
                collected_data={},
                lead_submitted=True,
                lead_record={"id": lead.id, "email": lead.email},
            )
        return FlowResult(
            state="ask_appointment_request",
            message="Please choose whether you would like a consultation request as well.",
            quick_replies=["Yes, request a consultation", "No, just send my details"],
            collected_data=data,
        )

    if state == "collect_preferred_date":
        if len(clean_message) < 3:
            return FlowResult(state="collect_preferred_date", message=date_prompt(), quick_replies=[], collected_data=data)
        data["preferred_date"] = clean_message
        return FlowResult(state="collect_preferred_time", message=time_prompt(), quick_replies=[], collected_data=data)

    if state == "collect_preferred_time":
        if len(clean_message) < 2:
            return FlowResult(state="collect_preferred_time", message=time_prompt(), quick_replies=[], collected_data=data)
        data["preferred_time"] = clean_message
        return FlowResult(state="collect_notes", message=notes_prompt(), quick_replies=["None"], collected_data=data)

    if state == "collect_notes":
        data["notes"] = "" if clean_message.lower() == "none" else clean_message
        lead = create_lead(session, data)
        appointment_request = create_appointment_request(session, data, lead.id)
        fallback = (
            "Thanks, your consultation request is received. A Northstar Solar team member will review your preferred time and contact you soon to confirm the next step."
        )
        answer = await ai_service.polish_message(fallback, "confirm_appointment_request")
        return FlowResult(
            state="detect_intent",
            message=answer,
            quick_replies=["Ask a question", "Request another consultation"],
            collected_data={},
            lead_submitted=True,
            appointment_requested=True,
            lead_record={"id": lead.id, "email": lead.email},
            appointment_record={"id": appointment_request.id, "status": appointment_request.status},
        )

    fallback = "I can help answer questions about Northstar Solar, collect your details, or submit a consultation request. How would you like to continue?"
    answer = await ai_service.polish_message(fallback, "fallback")
    return FlowResult(
        state="detect_intent",
        message=answer,
        quick_replies=["Ask a question", "Leave my details", "Request a consultation"],
        collected_data=data,
        needs_handoff=False,
    )
