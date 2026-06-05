# Wiring AI

Beginner-friendly electronics wiring assistant. Select catalog components, describe your project, and receive a **backend-verified** pin-level React Flow diagram with step-by-step instructions.

## Architecture

```
Catalog-constrained AI planning → Backend validation → React Flow graph → Frontend render
```

- **AI** plans compatibility and pin-level connections (catalog IDs only).
- **Backend** validates pins, voltages, and safety rules, then builds the graph.
- **Frontend** renders the approved diagram and instructions only.

## Stack

| Layer    | Tech                                      |
| -------- | ----------------------------------------- |
| Frontend | Next.js, TypeScript, React Flow, Zustand, Tailwind |
| Backend  | FastAPI, Pydantic, SQLModel, SQLite       |
| AI       | OpenAI (optional; mock planner without key) |

## Quick start

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Seed runs automatically on startup (78 components).

### Frontend

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

Open http://localhost:3000

### Tests

```bash
cd backend
pytest app/tests -q
```

## API

- `GET /api/components` — catalog list
- `GET /api/components/{id}` — component + pins
- `POST /api/ai/plan` — AI plan + validation + graph
- `POST /api/wiring/validate-ai-plan` — validate connections only

Set `OPENAI_API_KEY` in `backend/.env` for live LLM planning; otherwise a deterministic mock planner handles common beginner circuits and safety fallbacks.
