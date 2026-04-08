# Contributing

Thanks for improving this project.

## Development flow

1. Create a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env`.
4. Run the app with `python -m uvicorn app.main:app --reload`.
5. Run checks before opening a pull request.

## Recommended checks

- `python -m compileall app`
- `pytest`

## Commit style

- Keep commits focused and atomic.
- Prefer clear messages such as `feat: add admin stats route`.
- Update docs when behavior changes.

## Demo data

The bundled `Northstar Solar` content is fake and safe for demos. Replace `data/faqs.json` and UI copy before using the app for a real business.
