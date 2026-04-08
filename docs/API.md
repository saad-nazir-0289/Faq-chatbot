# API Guide

## Start chat

`POST /chat/start`

Returns a new session id, the opening assistant message, and suggested quick replies.

## Send message

`POST /chat/message`

Request body:

```json
{
  "session_id": "uuid",
  "message": "I need a quote"
}
```

The response contains the next chatbot message, current flow state, and flags for lead capture or consultation completion.

## FAQ list

`GET /faqs`

Useful during demos and for validating seeded content.

## Health

`GET /health`

Returns `ok` when the app boots successfully.
