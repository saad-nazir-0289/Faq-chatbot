# Support Chatbot

A FastAPI app with a built-in chat page that answers FAQs, collects lead information, and accepts appointment requests.

The current demo is preloaded with a fictional business called `Northstar Solar`, so it works out of the box with dummy content.

## Features

- FAQ answers backed by seeded data in `data/faqs.json`
- Structured conversation flow for lead capture and appointment requests
- AI-assisted response generation when `OPENAI_API_KEY` is configured
- SQLite persistence for conversations, leads, messages, and appointment requests
- Built-in responsive chat interface served from FastAPI
- Dummy FAQ, pricing, and consultation flows that work without external services

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Then open `http://127.0.0.1:8000`.

## API endpoints

- `GET /`
- `GET /health`
- `POST /chat/start`
- `POST /chat/message`
- `GET /faqs`

## Notes

- If no AI key is configured, the chatbot still works with deterministic responses.
- Appointment submissions are requests only. The app does not reserve live calendar slots in v1.
- Delete `support_chatbot.db` if you want to reset the demo data and reseed the bundled FAQs.
