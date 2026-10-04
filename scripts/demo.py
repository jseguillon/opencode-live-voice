import asyncio
from opencode_live_voice.backends.llm import MockNarrator
from opencode_live_voice.backends.tts import StdoutTTS
from opencode_live_voice.config import Settings
from opencode_live_voice.models import EventKind, VoiceEvent
from opencode_live_voice.opencode_client import OpenCodeClient
from opencode_live_voice.service import VoiceService


async def main():
    cfg = Settings(coalesce_ms=20)
    svc = VoiceService(cfg, MockNarrator(cfg), StdoutTTS(), OpenCodeClient(cfg))
    await svc.ingest(VoiceEvent(event=EventKind.SESSION_STARTED, session_id="demo", message="Fix API tests"))
    await svc.ingest(VoiceEvent(event=EventKind.TOOL_STARTED, session_id="demo", message="pytest"))
    await asyncio.sleep(0.05)
    await svc.ingest(VoiceEvent(event=EventKind.PERMISSION, session_id="demo", message="write outside project"))
    await svc.ingest(VoiceEvent(event=EventKind.COMPLETE, session_id="demo", message="all tests pass"))
    await asyncio.sleep(0.05)


asyncio.run(main())
