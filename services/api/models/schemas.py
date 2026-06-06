from pydantic import BaseModel, Field
from typing import Any


class AgentChatRequest(BaseModel):
    business_slug: str
    channel: str = Field(default="web", pattern="^(web|telegram|sms|whatsapp_manual)$")
    customer_ref: str | None = None
    message: str
    conversation_id: str | None = None


class AgentAction(BaseModel):
    type: str
    payload: dict[str, Any] = {}


class AgentChatResponse(BaseModel):
    conversation_id: str
    reply: str
    intent: str
    confidence: float
    actions: list[AgentAction] = []
    escalated: bool = False
    metadata: dict[str, Any] = {}


class IntentClassification(BaseModel):
    intent: str
    confidence: float
    entities: dict[str, str | None] = {}
    needs_clarification: bool = False
    clarification_question: str | None = None


class KnowledgeItem(BaseModel):
    type: str
    title: str
    content: str
    active: bool = True


class BusinessProfile(BaseModel):
    id: str
    name: str
    sector: str | None = None
    city: str | None = None
    tone: str | None = None
    language: str | None = None
    public_slug: str
    knowledge_items: list[KnowledgeItem] = []
    storage: str = "memory"
    knowledge_count: int = 0
