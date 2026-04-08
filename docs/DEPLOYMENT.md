# Deployment Checklist

## Before deploy

- replace the fake Northstar Solar data
- configure a real secret in `.env`
- move to PostgreSQL if you expect concurrent production traffic
- run tests and the smoke script

## Container deployment

```bash
docker build -t faq-chatbot .
docker run -p 8000:8000 --env-file .env faq-chatbot
```

## Managed platforms

Good fits for this app:

- Render
- Railway
- Fly.io
- Azure App Service

## Production notes

- add HTTPS termination with a reverse proxy or platform TLS
- enable request logging
- back up your database
- restrict admin endpoints before exposing them publicly
