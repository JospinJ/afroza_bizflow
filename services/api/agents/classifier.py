"""B2 — Intent classification via LLM + post-rules."""

import json
from pathlib import Path

from agents.groq_client import GroqRotatingClient
from models.schemas import IntentClassification

INTENTS = {
    "price_inquiry",
    "availability",
    "appointment",
    "quote_request",
    "payment_question",
    "complaint",
    "discount_request",
    "legal_question",
    "general_info",
    "greeting",
    "unknown",
}

ESCALATE_INTENTS = {"complaint", "discount_request", "legal_question"}
CONFIDENCE_THRESHOLD = 0.55

PROMPT_PATH = Path(__file__).parent / "prompts" / "intent_classifier.txt"


def _load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


async def classify_intent(
    client: GroqRotatingClient,
    message: str,
    history: list[dict],
    business_name: str,
    sector: str,
) -> IntentClassification:
    history_text = "\n".join(
        f"{m['role']}: {m['content']}" for m in history[-3:]
    )
    prompt = _load_prompt().format(
        business_name=business_name,
        sector=sector,
        user_message=message,
        history=history_text or "(aucun)",
    )

    completion = client.chat_completion(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        response_format={"type": "json_object"},
    )

    raw = completion.choices[0].message.content or "{}"
    data = json.loads(raw)

    intent = data.get("intent", "unknown")
    if intent not in INTENTS:
        intent = "unknown"

    return IntentClassification(
        intent=intent,
        confidence=float(data.get("confidence", 0.5)),
        entities=data.get("entities") or {},
        needs_clarification=bool(data.get("needs_clarification")),
        clarification_question=data.get("clarification_question"),
    )


def should_escalate(
    classification: IntentClassification,
    unknown_streak: int = 0,
) -> bool:
    if classification.intent in ESCALATE_INTENTS:
        return True
    if classification.confidence < CONFIDENCE_THRESHOLD:
        return True
    if classification.intent == "unknown" and unknown_streak >= 2:
        return True
    return False
