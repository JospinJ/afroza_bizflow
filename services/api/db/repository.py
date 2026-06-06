"""Accès données Agent IA via Supabase."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from db.supabase_client import get_supabase


def load_business_by_slug(slug: str) -> dict[str, Any] | None:
    sb = get_supabase()
    biz = sb.table("businesses").select("*").eq("public_slug", slug).eq("status", "active").limit(1).execute()
    if not biz.data:
        return None

    business = biz.data[0]
    items = (
        sb.table("knowledge_items")
        .select("type, title, content, active")
        .eq("business_id", business["id"])
        .eq("active", True)
        .execute()
    )
    business["knowledge_items"] = items.data or []
    return business


def load_message_history(conversation_id: str, limit: int = 10) -> list[dict[str, str]]:
    sb = get_supabase()
    rows = (
        sb.table("messages")
        .select("direction, content")
        .eq("conversation_id", conversation_id)
        .order("created_at")
        .limit(limit)
        .execute()
    )
    history: list[dict[str, str]] = []
    for row in rows.data or []:
        role = "user" if row["direction"] == "inbound" else "assistant"
        history.append({"role": role, "content": row["content"]})
    return history


def get_or_create_conversation(
    business_id: str,
    channel: str,
    conversation_id: str | None,
    customer_ref: str | None,
) -> tuple[str, dict[str, Any]]:
    sb = get_supabase()

    if conversation_id:
        conv = sb.table("conversations").select("*").eq("id", conversation_id).limit(1).execute()
        if conv.data:
            meta = conv.data[0].get("metadata") or {}
            return conversation_id, {
                "id": conversation_id,
                "unknown_streak": meta.get("unknown_streak", 0),
                "qualification_state": meta.get("qualification_state"),
            }

    cid = str(uuid.uuid4())
    sb.table("conversations").insert(
        {
            "id": cid,
            "business_id": business_id,
            "channel": channel,
            "status": "open",
            "metadata": {"unknown_streak": 0, "customer_ref": customer_ref},
        }
    ).execute()
    return cid, {"id": cid, "unknown_streak": 0, "qualification_state": None}


def save_message(
    conversation_id: str,
    direction: str,
    content: str,
    intent: str | None = None,
    confidence: float | None = None,
) -> None:
    sb = get_supabase()
    sb.table("messages").insert(
        {
            "conversation_id": conversation_id,
            "direction": direction,
            "content": content,
            "intent": intent,
            "confidence": confidence,
        }
    ).execute()
    sb.table("conversations").update(
        {"last_message_at": datetime.now(timezone.utc).isoformat()}
    ).eq("id", conversation_id).execute()


def update_conversation_meta(conversation_id: str, unknown_streak: int, status: str | None = None) -> None:
    sb = get_supabase()
    conv = sb.table("conversations").select("metadata").eq("id", conversation_id).limit(1).execute()
    meta = (conv.data[0].get("metadata") if conv.data else {}) or {}
    meta["unknown_streak"] = unknown_streak
    payload: dict[str, Any] = {"metadata": meta}
    if status:
        payload["status"] = status
    sb.table("conversations").update(payload).eq("id", conversation_id).execute()
