"""Business Memory / RAG — load knowledge_items for context injection."""

from dataclasses import dataclass


INTENT_TO_KNOWLEDGE_TYPES: dict[str, list[str]] = {
    "price_inquiry": ["service", "faq"],
    "availability": ["hours", "service"],
    "appointment": ["service", "hours", "policy"],
    "quote_request": ["service", "policy", "faq"],
    "payment_question": ["policy", "faq"],
    "general_info": ["faq", "service", "hours"],
    "greeting": ["tone"],
}


@dataclass
class KnowledgeContext:
    text: str
    item_count: int
    items: list[dict]
    matched_types: list[str]


def build_rag_context(
    knowledge_items: list[dict],
    intent: str,
    max_items: int = 5,
) -> KnowledgeContext:
    types = INTENT_TO_KNOWLEDGE_TYPES.get(intent, ["faq", "service", "hours", "policy"])
    filtered = [k for k in knowledge_items if k.get("type") in types and k.get("active", True)]
    selected = filtered[:max_items]

    if not selected:
        selected = knowledge_items[:max_items]

    lines = []
    for item in selected:
        lines.append(f"- [{item['type']}] {item['title']}: {item['content']}")

    header = "=== CONTEXTE PME ===\n" + "\n".join(lines) if lines else "=== CONTEXTE PME ===\n(Aucune donnée)"
    return KnowledgeContext(
        text=header,
        item_count=len(selected),
        items=selected,
        matched_types=types,
    )
