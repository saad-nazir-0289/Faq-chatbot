# Troubleshooting

## The UI opens but chat does not respond

- confirm the backend is running on port `8000`
- check browser dev tools for failing requests
- restart the app and clear local storage

## FAQ answers look generic

- confirm `data/faqs.json` contains the terms you are testing
- add an AI key if you want more natural phrasing

## I need a clean demo state

- run `python scripts/reset_demo.py`
- restart the application to reseed FAQs

## Tests fail because of missing packages

- rerun `pip install -r requirements.txt`
- make sure the same Python interpreter is used for running the app and tests
