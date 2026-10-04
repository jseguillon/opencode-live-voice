from __future__ import annotations

import json

import httpx

from ..config import Settings
from ..models import NarrationDecision, SessionState, VoiceEvent


SYSTEM = """You are the local voice interaction narrator for OpenCode.
The coding agent itself is remote and expensive. You NEVER solve coding tasks and NEVER invent actions.
Your only job is to turn trusted event/state data into a very short spoken update.
Do not narrate individual shell commands unless they materially change state.
Do not repeat the last spoken message.
Maximum 18 words normally. Output strict JSON: {\"speak\":bool,\"text\":str,\"priority\":\"normal|urgent\",\"interrupt\":bool}.
Permission, errors, and direct questions are urgent. If nothing meaningful changed, set speak=false.
"""


class LocalNarrator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def decide(self, state: SessionState, events: list[VoiceEvent]) -> NarrationDecision:
        payload = {
            "session": state.model_dump(),
            "new_events": [e.model_dump(mode="json") for e in events],
        }
        body = {
            "model": self.settings.local_llm_model,
            "messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            "temperature": 0.1,
            "max_tokens": 80,
            "response_format": {"type": "json_object"},
        }
        headers = {"Authorization": f"Bearer {self.settings.local_llm_api_key}"}
        async with httpx.AsyncClient(timeout=self.settings.local_llm_timeout_s) as client:
            r = await client.post(f"{self.settings.local_llm_base_url.rstrip('/')}/chat/completions", json=body, headers=headers)
            r.raise_for_status()
            content = r.json()["choices"][0]["message"]["content"]
        return NarrationDecision.model_validate_json(content)


class MockNarrator(LocalNarrator):
    async def decide(self, state: SessionState, events: list[VoiceEvent]) -> NarrationDecision:
        if not events:
            return NarrationDecision(speak=False)
        last = events[-1]
        if last.event.value == "permission":
            return NarrationDecision(speak=True, text="OpenCode needs permission to continue.", priority="urgent", interrupt=True)
        if last.event.value == "error":
            return NarrationDecision(speak=True, text="The coding agent hit an error.", priority="urgent", interrupt=True)
        if last.event.value in {"complete", "subagent_complete"}:
            return NarrationDecision(speak=True, text="The task is complete.")
        if last.event.value == "tool_started":
            return NarrationDecision(speak=True, text="The agent is working on the requested change.")
        return NarrationDecision(speak=False)
