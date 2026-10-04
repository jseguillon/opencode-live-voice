from __future__ import annotations

import httpx
from .config import Settings


class OpenCodeClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def abort(self, session_id: str) -> None:
        async with httpx.AsyncClient(timeout=self.settings.opencode_timeout_s) as client:
            r = await client.post(f"{self.settings.opencode_base_url.rstrip('/')}/session/{session_id}/abort")
            r.raise_for_status()

    async def prompt(self, session_id: str, text: str) -> None:
        payload = {"parts": [{"type": "text", "text": text}]}
        async with httpx.AsyncClient(timeout=self.settings.opencode_timeout_s) as client:
            r = await client.post(f"{self.settings.opencode_base_url.rstrip('/')}/session/{session_id}/message", json=payload)
            r.raise_for_status()

    async def permission(self, session_id: str, permission_id: str, reply: str) -> None:
        payload = {"reply": reply}
        async with httpx.AsyncClient(timeout=self.settings.opencode_timeout_s) as client:
            r = await client.post(
                f"{self.settings.opencode_base_url.rstrip('/')}/session/{session_id}/permission/{permission_id}", json=payload
            )
            r.raise_for_status()
