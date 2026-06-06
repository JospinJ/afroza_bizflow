"""Client Groq avec rotation de clés API (GROQ_API_KEY séparées par des virgules)."""

import os
from typing import Any

from groq import (
    APIStatusError,
    AuthenticationError,
    Groq,
    PermissionDeniedError,
    RateLimitError,
)

ROTATABLE_STATUS_CODES = {401, 403, 429}
_current_key_index = 0


def parse_groq_api_keys() -> list[str]:
    raw = os.getenv("GROQ_API_KEY", "").strip()
    if not raw:
        return []
    return [
        key.strip()
        for key in raw.split(",")
        if key.strip() and not key.strip().startswith("your_")
    ]


def _is_rotatable_error(exc: Exception) -> bool:
    if isinstance(exc, (RateLimitError, AuthenticationError, PermissionDeniedError)):
        return True
    if isinstance(exc, APIStatusError):
        return exc.status_code in ROTATABLE_STATUS_CODES
    return False


class GroqRotatingClient:
    def __init__(self) -> None:
        self._keys = parse_groq_api_keys()
        if not self._keys:
            raise RuntimeError(
                "GROQ_API_KEY manquant — voir services/api/.env "
                "(plusieurs clés possibles, séparées par des virgules)"
            )
        global _current_key_index
        self._index = _current_key_index % len(self._keys)
        self._client = Groq(api_key=self._keys[self._index])

    @property
    def active_key_index(self) -> int:
        return self._index + 1

    @property
    def keys_count(self) -> int:
        return len(self._keys)

    def _rotate(self) -> bool:
        if len(self._keys) <= 1:
            return False
        global _current_key_index
        self._index = (self._index + 1) % len(self._keys)
        _current_key_index = self._index
        self._client = Groq(api_key=self._keys[self._index])
        return True

    def chat_completion(self, **kwargs: Any):
        last_exc: Exception | None = None
        for _ in range(len(self._keys)):
            try:
                return self._client.chat.completions.create(**kwargs)
            except Exception as exc:
                if not _is_rotatable_error(exc):
                    raise
                last_exc = exc
                if not self._rotate():
                    raise
        if last_exc:
            raise last_exc
        raise RuntimeError("Aucune clé Groq disponible")


def get_groq_client() -> GroqRotatingClient:
    return GroqRotatingClient()
