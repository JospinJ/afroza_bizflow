"""Afroza BizFlow — Agent IA API (B1-B6)."""

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Toujours charger .env depuis ce dossier (meme si uvicorn est lance ailleurs)
load_dotenv(Path(__file__).resolve().parent / ".env")

from routers.agents import router as agents_router

app = FastAPI(
    title="Afroza BizFlow Agent API",
    description="Module Agent IA — orchestrator, intents, RAG, qualification, RDV, escalade",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agents_router, prefix="/api/agents", tags=["agents"])


@app.get("/health")
def health():
    from db.supabase_client import is_supabase_configured

    return {
        "status": "ok",
        "module": "agent_ia",
        "supabase": is_supabase_configured(),
    }
