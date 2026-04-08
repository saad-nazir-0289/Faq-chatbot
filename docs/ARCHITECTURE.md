# Architecture

## Layers

- `app/api/routes` exposes HTTP endpoints.
- `app/services` contains the chatbot flow and supporting business logic.
- `app/db` defines persistence models and session helpers.
- `app/static` serves the built-in frontend.

## Chat flow

1. The browser starts a session with `POST /chat/start`.
2. The backend stores the conversation in SQLite.
3. Each user message is routed through the flow engine.
4. The engine either answers an FAQ, collects lead fields, or captures a consultation request.
5. Optional AI phrasing makes responses feel more natural.

## Persistence

- `Conversation` tracks session state.
- `Message` stores the transcript.
- `Lead` stores qualified visitor information.
- `AppointmentRequest` stores consultation requests.
