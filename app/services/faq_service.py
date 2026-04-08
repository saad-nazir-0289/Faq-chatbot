from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List

from sqlmodel import Session, select

from app.db.models import FAQ


FAQ_FILE = Path("data/faqs.json")


def tokenize(value: str) -> set[str]:
    return {term for term in re.findall(r"[a-z0-9]+", value.lower()) if len(term) > 2}


def seed_faqs(session: Session) -> None:
    existing = session.exec(select(FAQ)).first()
    if existing or not FAQ_FILE.exists():
        return

    payload = json.loads(FAQ_FILE.read_text(encoding="utf-8"))
    for item in payload:
        session.add(
            FAQ(
                question=item["question"],
                answer=item["answer"],
                tags=",".join(item.get("tags", [])),
                active=item.get("active", True),
            )
        )
    session.commit()


def get_all_faqs(session: Session) -> List[FAQ]:
    return list(session.exec(select(FAQ).where(FAQ.active == True)))


def search_faqs(session: Session, user_message: str, limit: int = 3) -> List[FAQ]:
    faqs = get_all_faqs(session)
    query_terms = tokenize(user_message)
    scored = []
    for faq in faqs:
        haystack = f"{faq.question} {faq.answer} {faq.tags}".lower()
        haystack_terms = tokenize(haystack)
        overlap = len(query_terms & haystack_terms)
        partial_hits = sum(1 for term in query_terms if term in haystack)
        score = overlap * 3 + partial_hits
        if score:
            scored.append((score, faq))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [faq for _, faq in scored[:limit]]
