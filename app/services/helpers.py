from __future__ import annotations

import json
import re
from typing import Any, Dict

from pydantic import EmailStr, TypeAdapter


EMAIL_ADAPTER = TypeAdapter(EmailStr)


def loads_json(value: str) -> Dict[str, Any]:
    if not value:
        return {}
    return json.loads(value)


def dumps_json(value: Dict[str, Any]) -> str:
    return json.dumps(value)


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def looks_like_yes(value: str) -> bool:
    cleaned = value.lower().strip()
    yes_terms = ["yes", "yeah", "yep", "sure", "ok", "okay", "please", "book a call", "book a meeting", "book", "schedule"]
    return any(term in cleaned for term in yes_terms)


def looks_like_no(value: str) -> bool:
    cleaned = value.lower().strip()
    no_terms = ["no", "nope", "not now", "later", "just browsing", "just send", "send my details"]
    return any(term in cleaned for term in no_terms)


def validate_email(value: str) -> bool:
    try:
        EMAIL_ADAPTER.validate_python(value)
        return bool(re.fullmatch(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", value, re.IGNORECASE))
    except Exception:
        return False


def validate_phone(value: str) -> bool:
    digits = re.sub(r"\D", "", value)
    return len(digits) >= 7


def extract_email(value: str) -> str:
    match = re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", value, re.IGNORECASE)
    return match.group(0) if match else ""


def extract_phone(value: str) -> str:
    match = re.search(r"\+?[\d\s().-]{7,}", value)
    return normalize_text(match.group(0)) if match else ""
