"""Client Supabase — singleton lazy."""

import os

from supabase import Client, create_client

_client: Client | None = None


def is_supabase_configured() -> bool:
    url = os.getenv("SUPABASE_URL", "").strip()
    key = (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        or os.getenv("SUPABASE_SECRET_KEY", "").strip()
    )
    return bool(url and key and not key.startswith("your_"))


def get_supabase() -> Client:
    global _client
    if _client is not None:
        return _client

    url = os.getenv("SUPABASE_URL", "").strip()
    key = (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        or os.getenv("SUPABASE_SECRET_KEY", "").strip()
    )
    if not url or not key:
        raise RuntimeError(
            "Supabase non configuré — renseignez SUPABASE_URL et "
            "SUPABASE_SERVICE_ROLE_KEY dans services/api/.env"
        )
    _client = create_client(url, key)
    return _client
