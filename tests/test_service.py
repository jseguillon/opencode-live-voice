import asyncio
import pytest

from opencode_live_voice.config import Settings
from opencode_live_voice.models import EventKind, NarrationDecision, VoiceEvent
from opencode_live_voice.service import VoiceService


class Narrator:
    def __init__(self):
        self.calls = []

    async def decide(self, state, events):
        self.calls.append(list(events))
        return NarrationDecision(speak=True, text=f"{len(events)} events")


class TTS:
    def __init__(self):
        self.spoken = []

    async def speak(self, text, interrupt=False):
        self.spoken.append((text, interrupt))

    async def stop(self):
        pass


class OpenCode:
    async def abort(self, session_id):
        pass

    async def prompt(self, session_id, text):
        pass


@pytest.mark.asyncio
async def test_events_are_coalesced():
    narrator, tts = Narrator(), TTS()
    svc = VoiceService(Settings(coalesce_ms=20), narrator, tts, OpenCode())
    await svc.ingest(VoiceEvent(event=EventKind.TOOL_STARTED, session_id="s", message="read"))
    await svc.ingest(VoiceEvent(event=EventKind.TOOL_FINISHED, session_id="s", message="read"))
    await asyncio.sleep(0.05)
    assert len(narrator.calls) == 1
    assert len(narrator.calls[0]) == 2
    assert tts.spoken == [("2 events", False)]
