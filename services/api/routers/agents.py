from fastapi import APIRouter, HTTPException

from agents.orchestrator import handle_chat, load_business_profile
from agents.rag import INTENT_TO_KNOWLEDGE_TYPES, build_rag_context
from models.schemas import AgentChatRequest, AgentChatResponse, BusinessProfile

router = APIRouter()


@router.get("/business/{slug}", response_model=BusinessProfile)
def get_business(slug: str) -> BusinessProfile:
    profile = load_business_profile(slug)
    if not profile:
        raise HTTPException(status_code=404, detail="Salon introuvable")
    return profile


@router.get("/business/{slug}/rag-preview")
def rag_preview(slug: str, intent: str = "general_info") -> dict:
    profile = load_business_profile(slug)
    if not profile:
        raise HTTPException(status_code=404, detail="Salon introuvable")

    items = [item.model_dump() for item in profile.knowledge_items]
    rag = build_rag_context(items, intent)
    return {
        "intent": intent,
        "matched_types": rag.matched_types,
        "available_intents": sorted(INTENT_TO_KNOWLEDGE_TYPES.keys()),
        "selected_items": rag.items,
        "context_preview": rag.text,
    }


@router.post("/chat", response_model=AgentChatResponse)
async def chat(request: AgentChatRequest) -> AgentChatResponse:
    try:
        return await handle_chat(request)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
