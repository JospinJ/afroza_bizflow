"""B1 — Agent orchestrator: routes message through classify → act → respond."""

import os
import time
import uuid
from pathlib import Path

from agents.classifier import classify_intent, should_escalate
from agents.groq_client import get_groq_client
from agents.escalation import build_escalation_response
from agents.rag import build_rag_context
from db.supabase_client import is_supabase_configured
from models.schemas import AgentAction, AgentChatRequest, AgentChatResponse, BusinessProfile, KnowledgeItem

SYSTEM_PROMPT_PATH = Path(__file__).parent / "prompts" / "system_agent.txt"

_DEMO_BUSINESS = {
    "id": "demo-salon-aicha",
    "name": "Salon Aïcha",
    "sector": "coiffure",
    "tone": "chaleureux",
    "language": "fr",
    "public_slug": "salon-aicha",
    "knowledge_items": [
        {"type": "service", "title": "Braids", "content": "15000 FCFA, durée 3h, acompte 5000 FCFA", "active": True},
        {"type": "service", "title": "Tissage", "content": "12000 FCFA, durée 2h30", "active": True},
        {"type": "hours", "title": "Horaires", "content": "Lundi-Samedi 9h-19h, Dimanche fermé", "active": True},
        {"type": "policy", "title": "Acompte", "content": "50% à la réservation, annulation 24h avant", "active": True},
        {"type": "faq", "title": "Paiement", "content": "Mobile Money accepté. Mode simulation active en démo.", "active": True},
    ],
}

_conversations: dict[str, dict] = {}


def _load_business(slug: str) -> tuple[dict | None, str]:
    if is_supabase_configured():
        from db.repository import load_business_by_slug

        business = load_business_by_slug(slug)
        if business:
            return business, "supabase"
        return None, "supabase"

    if slug == _DEMO_BUSINESS["public_slug"]:
        return _DEMO_BUSINESS, "memory"
    return None, "memory"


def _get_or_create_conversation(
    request: AgentChatRequest,
    business: dict,
    business_storage: str,
) -> tuple[str, dict, list[dict], str]:
    if business_storage == "supabase":
        from db.repository import get_or_create_conversation, load_message_history

        conv_id, conv = get_or_create_conversation(
            business_id=business["id"],
            channel=request.channel,
            conversation_id=request.conversation_id,
            customer_ref=request.customer_ref,
        )
        history = load_message_history(conv_id)
        return conv_id, conv, history, "supabase"

    if request.conversation_id and request.conversation_id in _conversations:
        conv = _conversations[request.conversation_id]
        return request.conversation_id, conv, conv["history"], "memory"

    cid = str(uuid.uuid4())
    _conversations[cid] = {"history": [], "unknown_streak": 0, "qualification_state": None}
    return cid, _conversations[cid], _conversations[cid]["history"], "memory"


def _persist_turn(
    conv_id: str,
    conv: dict,
    user_message: str,
    reply: str,
    intent: str,
    confidence: float,
    escalated: bool,
    storage: str,
) -> None:
    if storage != "supabase":
        return
    from db.repository import save_message, update_conversation_meta

    save_message(conv_id, "inbound", user_message, intent=intent, confidence=confidence)
    save_message(conv_id, "outbound", reply, intent=intent, confidence=confidence)
    update_conversation_meta(
        conv_id,
        conv["unknown_streak"],
        status="escalated" if escalated else None,
    )


def load_business_profile(slug: str) -> BusinessProfile | None:
    business, storage = _load_business(slug)
    if not business:
        return None

    items = [
        KnowledgeItem(
            type=item["type"],
            title=item["title"],
            content=item["content"],
            active=item.get("active", True),
        )
        for item in business.get("knowledge_items", [])
    ]
    return BusinessProfile(
        id=str(business["id"]),
        name=business["name"],
        sector=business.get("sector"),
        city=business.get("city"),
        tone=business.get("tone"),
        language=business.get("language"),
        public_slug=business.get("public_slug", slug),
        knowledge_items=items,
        storage=storage,
        knowledge_count=len(items),
    )


async def handle_chat(request: AgentChatRequest) -> AgentChatResponse:
    start = time.time()
    business, business_storage = _load_business(request.business_slug)

    if not business:
        return AgentChatResponse(
            conversation_id=request.conversation_id or str(uuid.uuid4()),
            reply="Désolé, ce salon n'existe pas encore.",
            intent="unknown",
            confidence=1.0,
        )

    conv_id, conv, history, conv_storage = _get_or_create_conversation(
        request, business, business_storage
    )
    storage = conv_storage
    history.append({"role": "user", "content": request.message})

    client = get_groq_client()
    classification = await classify_intent(
        client=client,
        message=request.message,
        history=history,
        business_name=business["name"],
        sector=business["sector"],
    )

    if classification.intent == "unknown":
        conv["unknown_streak"] += 1
    else:
        conv["unknown_streak"] = 0

    if should_escalate(classification, conv["unknown_streak"]):
        summary = f"Intent: {classification.intent}, msg: {request.message[:200]}"
        response = build_escalation_response(conv_id, business["name"], classification, summary)
        _persist_turn(conv_id, conv, request.message, response.reply, classification.intent, classification.confidence, True, storage)
        return response

    actions: list[AgentAction] = []
    rag = build_rag_context(business["knowledge_items"], classification.intent)

    system = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8").format(
        business_name=business["name"],
        sector=business["sector"],
        tone=business["tone"],
        language=business["language"],
        payment_mode=os.getenv("PAYMENT_MODE", "simulated"),
        partner_finance_enabled="false",
        rag_context=rag.text,
    )

    completion = client.chat_completion(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system},
            *[{"role": h["role"], "content": h["content"]} for h in history[-6:]],
        ],
        temperature=0.4,
    )

    reply = completion.choices[0].message.content or "Je n'ai pas pu répondre."

    if classification.intent == "appointment":
        actions.append(AgentAction(
            type="propose_slots",
            payload={
                "slots": ["2026-06-07T10:00:00", "2026-06-07T14:00:00"],
                "service": classification.entities.get("service") or "braids",
            },
        ))

    if classification.intent == "quote_request":
        actions.append(AgentAction(type="start_qualification", payload={"stage": "collect_need"}))

    if storage != "supabase":
        conv["history"].append({"role": "assistant", "content": reply})

    _persist_turn(conv_id, conv, request.message, reply, classification.intent, classification.confidence, False, storage)

    latency_ms = int((time.time() - start) * 1000)
    return AgentChatResponse(
        conversation_id=conv_id,
        reply=reply,
        intent=classification.intent,
        confidence=classification.confidence,
        actions=actions,
        escalated=False,
        metadata={
            "latency_ms": latency_ms,
            "rag_items_used": rag.item_count,
            "rag_source": business_storage,
            "rag_matched_types": rag.matched_types,
            "rag_items": rag.items,
            "rag_context_preview": rag.text,
            "model": "llama-3.3-70b-versatile",
            "storage": storage,
        },
    )
