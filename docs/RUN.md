# How to run the demo locally

You need Python 3.10+ installed.

## Backend
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate     Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env        # Windows: copy ..\.env.example .env
uvicorn main:app --reload --port 8000
```
Open http://localhost:8000/docs to try the API. With `MOCK_AI=1` in `.env` it returns a sample result without any API key.
To score real videos, set `MOCK_AI=0` and put your `GEMINI_API_KEY` in `.env`. Never commit `.env`.

## Frontend
In a second terminal:
```bash
cd frontend
python -m http.server 5500
```
Open http://localhost:5500 in the browser.
