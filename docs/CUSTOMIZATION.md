# Customization Guide

## Rebrand the demo

- update `app/static/index.html`
- update `app/services/chatbot.py`
- update `data/faqs.json`

## Change the form flow

Edit `app/services/flow_engine.py` to:

- rename prompts
- collect extra fields
- change quick replies
- swap consultation wording for booking wording

## Add integrations

Common next steps:

- push leads to a CRM
- send appointment requests to email
- trigger Slack alerts for hot leads
