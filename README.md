# API Gateway (Groq + LiteLLM + FastAPI)

Small local setup for testing a model gateway and a simple multi-step orchestrator.

- `litellm` on `http://localhost:4000`
- `orchestrator` on `http://localhost:8000`

## What this does

`orchestrator` receives a task, calls the model a few times (planner/researcher/reviewer), and returns one final response.

## Prerequisites

- Docker Desktop
- Groq API key

## Setup

Copy `.env.example` to `.env`, then fill it in:

```env
GROQ_API_KEY=your_groq_key
LITELLM_MASTER_KEY=sk-1234
```

## Run

```bash
docker compose up -d --build
docker compose ps
```

Both services should show `Up`.

## Quick test

Health check:

```bash
curl http://localhost:8000/health
```

Expected:

```json
{"ok":true}
```

End-to-end request:

```bash
curl -X POST http://localhost:8000/run -H "Content-Type: application/json" -d "{\"task\":\"Give me 3 launch steps for an API gateway\"}"
```

If it works, the response includes `planner`, `researcher`, and `final`.

Direct LiteLLM check:

```bash
curl -X POST http://localhost:4000/v1/chat/completions -H "Authorization: Bearer sk-1234" -H "Content-Type: application/json" -d "{\"model\":\"my-fast-model\",\"messages\":[{\"role\":\"user\",\"content\":\"Say hello in one line\"}]}"
```

## Stop

```bash
docker compose down
```

## Notes

- Keep `.env` out of git.
- Rotate your key if it was ever shared.
