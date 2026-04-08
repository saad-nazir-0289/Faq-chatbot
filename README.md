# Faq-chatbot

`Faq-chatbot` is a FastAPI chatbot starter built for businesses that need always-on customer support.

The bundled demo ships with a fictional company called `Northstar Solar`, so you can run the app immediately, test realistic flows, and then swap the dummy content with your own business details.

## What it does

- answers FAQ-style questions from seeded business content
- collects lead details in a structured flow
- accepts appointment or consultation requests
- stores conversations, leads, and requests in SQLite
- serves a built-in responsive web chat UI
- works without an external AI key using deterministic fallback responses

## Demo business included

The current experience is preloaded with fake content for `Northstar Solar`:

- solar installation FAQs
- pricing and install timeline examples
- residential and commercial inquiry flows
- consultation request capture

## Tech stack

- FastAPI
- SQLModel + SQLite
- Pydantic Settings
- Vanilla HTML, CSS, and JavaScript frontend
- Optional OpenAI-compatible API integration

## Project structure

```text
app/
  api/routes/        API endpoints
  core/              settings and app config
  db/                SQLModel models and session management
  schemas/           request and response schemas
  services/          chatbot logic and business services
  static/            built-in web UI
data/
  faqs.json          seeded demo FAQ content
docs/                developer and deployment guides
scripts/             helper scripts for local workflows
tests/               API and flow tests
```

## Quick start

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload
```

### macOS or Linux

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

## Environment variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `APP_NAME` | no | UI and OpenAPI title |
| `APP_ENV` | no | environment label |
| `DATABASE_URL` | no | SQLite or another SQLAlchemy-compatible URL |
| `OPENAI_API_KEY` | no | enables AI-generated phrasing |
| `OPENAI_BASE_URL` | no | custom OpenAI-compatible endpoint |
| `OPENAI_MODEL` | no | model name for chat completions |

## API endpoints

- `GET /` - built-in chat page
- `GET /health` - health status
- `POST /chat/start` - start a conversation session
- `POST /chat/message` - send a user message
- `GET /faqs` - inspect seeded FAQ content

## How to make it work like a pro

### 1. Replace the demo business

- update `data/faqs.json` with real questions and answers
- replace `Northstar Solar` copy in `app/static/index.html` and `app/services/chatbot.py`
- tune field prompts in `app/services/flow_engine.py`

### 2. Set a real AI provider

- add your key to `.env`
- point `OPENAI_BASE_URL` to your provider if you use an OpenAI-compatible service
- pick a fast, low-cost model for production chat

### 3. Move beyond SQLite

- use PostgreSQL in production
- set `DATABASE_URL` to your managed database
- keep SQLite only for local demos and quick testing

### 4. Wire in your operations stack

- send new leads to your CRM
- forward consultation requests to your sales inbox
- add calendar integration if you need live booking

### 5. Protect admin and data flows

- add authentication before exposing internal dashboards
- log failed requests and validation errors
- rotate API keys and never commit `.env`

### 6. Validate before deployment

- run `python -m compileall app`
- run `pytest`
- run `python scripts/smoke_test.py`

## Developer workflow

```bash
python -m compileall app
pytest
python scripts/smoke_test.py
```

## Resetting demo data

- delete `support_chatbot.db`, or
- run `python scripts/reset_demo.py`

## Deployment ideas

- Docker container on Render, Railway, Fly.io, or Azure App Service
- reverse proxy with Nginx or Caddy
- managed PostgreSQL + secret manager for production credentials

See `docs/DEPLOYMENT.md` for a more practical deployment checklist.

## Notes

- if no AI key is configured, the chatbot still works
- consultation submissions are requests only in this demo
- the bundled data is fake and intended for demos and development

## License

MIT
