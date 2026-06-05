# Wiring AI Architecture

## Flow

```
User input (description + selected components)
  → Backend loads catalog context
  → AI returns structured JSON plan
  → Pydantic + backend validator
  → Graph builder (React Flow nodes/edges)
  → Frontend renders diagram + steps
```

## Principles

1. **AI plans** — compatibility, missing parts, pin connections, steps.
2. **Backend verifies** — component/pin IDs, connection types, safety rules.
3. **Frontend renders** — no electrical logic on the client.

## Repositories

- `backend/app/seed/catalog_data.py` — 78 seeded components
- `backend/app/services/ai_wiring_planner_service.py` — OpenAI or mock planner
- `backend/app/services/backend_plan_validator_service.py` — strict validation
- `backend/app/services/graph_builder_service.py` — AI connections → React Flow
- `frontend/src/components/builder/` — builder UX
- `frontend/src/components/flow/` — custom React Flow nodes
