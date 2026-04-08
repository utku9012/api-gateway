import os

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="AI Orchestrator")
GATEWAY_URL = os.getenv("LLM_GATEWAY_URL", "http://litellm:4000/v1/chat/completions")
GATEWAY_KEY = os.getenv("LLM_GATEWAY_KEY") or os.getenv("LITELLM_MASTER_KEY")


class RunRequest(BaseModel):
    task: str


async def call_model(model_alias: str, prompt: str) -> str:
    payload = {
        "model": model_alias,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }
    headers = {}
    if GATEWAY_KEY:
        headers["Authorization"] = f"Bearer {GATEWAY_KEY}"
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(GATEWAY_URL, json=payload, headers=headers)
        if response.status_code >= 400:
            raise HTTPException(status_code=502, detail=response.text)
        body = response.json()
    return body["choices"][0]["message"]["content"]


@app.get("/health")
async def health() -> dict:
    return {"ok": True}


@app.post("/run")
async def run_agents(request: RunRequest) -> dict:
    task = request.task.strip()
    if not task:
        raise HTTPException(status_code=400, detail="task is required")

    planner = await call_model("my-fast-model", f"Create a short plan for: {task}")
    researcher = await call_model("my-fast-model", f"Find key facts for: {task}")
    reviewer_prompt = (
        f"Task: {task}\n"
        f"Plan: {planner}\n"
        f"Facts: {researcher}\n"
        "Return a final validated answer."
    )
    final_answer = await call_model("my-fast-model", reviewer_prompt)

    return {
        "task": task,
        "planner": planner,
        "researcher": researcher,
        "final": final_answer,
    }
