from __future__ import annotations

import json
from pathlib import Path
from typing import List

from sqlmodel import Session, select

from app.db.models import FAQ


FAQ_FILE = Path("data/faqs.json")


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
    query_terms = {term.lower() for term in user_message.split() if len(term) > 2}
    scored = []
    for faq in faqs:
        haystack = f"{faq.question} {faq.answer} {faq.tags}".lower()
        score = sum(1 for term in query_terms if term in haystack)
        if score:
            scored.append((score, faq))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [faq for _, faq in scored[:limit]]
