from __future__ import annotations

import asyncio
from collections import defaultdict

from .backends.llm import LocalNarrator
from .backends.tts import TTS
from .config import Settings
from .models import IntentKind, RoutedIntent, VoiceEvent
from .opencode_client import OpenCodeClient
from .router import route_text
from .state import StateStore


class VoiceService:
    def __init__(self, settings: Settings, narrator: LocalNarrator, tts: TTS, opencode: OpenCodeClient) -> None:
        self.settings = settings
        self.narrator = narrator
        self.tts = tts
        self.opencode = opencode
        self.state = StateStore(settings.max_recent_events)
        self._buffers: dict[str, list[VoiceEvent]] = defaultdict(list)
        self._tasks: dict[str, asyncio.Task[None]] = {}

    async def ingest(self, event: VoiceEvent) -> None:
        state = self.state.update(event)
        if not state or not event.session_id:
            return
        sid = event.session_id
        self._buffers[sid].append(event)
        if event.event.value in {"permission", "error", "question"}:
            await self._flush(sid)
            return
        old = self._tasks.get(sid)
        if old and not old.done():
            old.cancel()
        self._tasks[sid] = asyncio.create_task(self._flush_later(sid))

    async def _flush_later(self, sid: str) -> None:
        try:
            await asyncio.sleep(self.settings.coalesce_ms / 1000)
            await self._flush(sid)
        except asyncio.CancelledError:
            return

    async def _flush(self, sid: str) -> None:
        events = self._buffers.pop(sid, [])
        if not events:
            return
        state = self.state.get(sid)
        decision = await self.narrator.decide(state, events)
        if decision.speak and not state.muted:
            await self.tts.speak(decision.text, interrupt=decision.interrupt)
            state.last_spoken = decision.text

    async def utterance(self, text: str, session_id: str) -> RoutedIntent:
        intent = route_text(text, session_id)
        state = self.state.get(session_id)
        if intent.kind == IntentKind.STOP:
            await self.tts.stop()
            await self.opencode.abort(session_id)
        elif intent.kind == IntentKind.MUTE:
            state.muted = True
            await self.tts.stop()
        elif intent.kind == IntentKind.UNMUTE:
            state.muted = False
        elif intent.kind == IntentKind.REPEAT:
            if state.last_spoken and not state.muted:
                await self.tts.speak(state.last_spoken)
        elif intent.kind in {IntentKind.STATUS, IntentKind.SUMMARIZE}:
            summary = state.last_spoken or f"OpenCode is {state.phase}."
            if not state.muted:
                await self.tts.speak(summary)
        elif intent.kind == IntentKind.QUIETER:
            # Preference is local-only; later narration prompts can consume this setting.
            pass
        elif intent.kind in {IntentKind.ALLOW_ONCE, IntentKind.ALLOW_ALWAYS, IntentKind.DENY}:
            # Permission IDs come from structured permission events; spoken approval alone is intentionally insufficient.
            pass
        else:
            await self.opencode.prompt(session_id, text)
        return intent
