"""B5 — Human escalation."""

from models.schemas import AgentChatResponse, IntentClassification


def build_escalation_response(
    conversation_id: str,
    business_name: str,
    classification: IntentClassification,
    summary: str,
) -> AgentChatResponse:
    reply = (
        f"Je transmets votre demande à {business_name}. "
        "Elle vous répondra sous peu. Merci pour votre patience."
    )
    return AgentChatResponse(
        conversation_id=conversation_id,
        reply=reply,
        intent=classification.intent,
        confidence=classification.confidence,
        escalated=True,
        metadata={
            "manager_summary": summary,
            "priority": "high" if classification.intent in {"complaint", "legal_question"} else "medium",
        },
    )
