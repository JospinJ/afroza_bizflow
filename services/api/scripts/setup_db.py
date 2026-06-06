"""Seed Salon Aïcha via API Supabase (tables doivent exister)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)


def seed_via_api() -> None:
    from db.repository import load_business_by_slug
    from db.supabase_client import get_supabase, is_supabase_configured

    if not is_supabase_configured():
        print("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY manquants.")
        sys.exit(1)

    sb = get_supabase()
    try:
        existing = sb.table("businesses").select("id").eq("public_slug", "salon-aicha").limit(1).execute()
    except Exception as e:
        if "PGRST205" in str(e) or "businesses" in str(e):
            print("ERREUR: tables absentes.")
            print("Executez supabase/ALL_IN_ONE.sql dans Supabase SQL Editor -> Run")
            sys.exit(1)
        raise
    if existing.data:
        print("Seed déjà présent (salon-aicha).")
        loaded = load_business_by_slug("salon-aicha")
        print(f"OK — {len(loaded['knowledge_items'])} knowledge_items.")
        return

    biz = sb.table("businesses").insert(
        {
            "name": "Salon Aïcha",
            "sector": "coiffure",
            "city": "Abidjan",
            "tone": "chaleureux",
            "language": "fr",
            "public_slug": "salon-aicha",
            "country": "CI",
        }
    ).execute()
    business_id = biz.data[0]["id"]
    items = [
        ("service", "Braids", "15000 FCFA, durée 3h, acompte 5000 FCFA"),
        ("service", "Tissage", "12000 FCFA, durée 2h30"),
        ("hours", "Horaires", "Lundi-Samedi 9h-19h, Dimanche fermé"),
        ("policy", "Acompte", "50% à la réservation, annulation 24h avant"),
        ("faq", "Paiement", "Mobile Money accepté. Mode simulation active en démo."),
    ]
    sb.table("knowledge_items").insert(
        [{"business_id": business_id, "type": t, "title": title, "content": content} for t, title, content in items]
    ).execute()
    print("Seed Salon Aïcha inséré.")


if __name__ == "__main__":
    seed_via_api()
