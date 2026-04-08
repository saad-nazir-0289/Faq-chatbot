from __future__ import annotations

from typing import Iterable, List

import httpx

from app.core.config import get_settings


settings = get_settings()


class AIService:
    def __init__(self) -> None:
        self.enabled = bool(settings.openai_api_key)

    async def generate_response(self, system_prompt: str, user_prompt: str, fallback: str) -> str:
        if not self.enabled:
            return fallback

        url = settings.openai_base_url.rstrip("/") + "/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.openai_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.5,
        }
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
            body = response.json()
            return body["choices"][0]["message"]["content"].strip()
        except Exception:
            return fallback

    async def draft_faq_answer(self, user_message: str, faq_entries: Iterable[object], fallback: str) -> str:
        faq_lines: List[str] = []
        for faq in faq_entries:
            faq_lines.append(f"Q: {faq.question}\nA: {faq.answer}")
        faq_context = "\n\n".join(faq_lines)
        system_prompt = (
            "You are a customer support assistant. Answer only from the provided FAQ context. "
            "Be concise, warm, and practical. If the context is weak, suggest booking a call."
        )
        user_prompt = f"Customer question: {user_message}\n\nFAQ context:\n{faq_context}"
        return await self.generate_response(system_prompt, user_prompt, fallback)

    async def polish_message(self, fallback: str, intent: str) -> str:
        system_prompt = (
            "You are a helpful business support chatbot. Rewrite the message to sound natural, concise, and confident. "
            "Preserve all details and keep the wording suitable for a website chat widget."
        )
        user_prompt = f"Intent: {intent}\nMessage: {fallback}"
        return await self.generate_response(system_prompt, user_prompt, fallback)


ai_service = AIService()
