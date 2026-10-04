from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .backends.llm import LocalNarrator, MockNarrator
from .backends.tts import CommandTTS, PiperTTS, StdoutTTS
from .config import Settings, settings
from .models import VoiceEvent
from .opencode_client import OpenCodeClient
from .service import VoiceService


class Utterance(BaseModel):
    session_id: str
    text: str


def create_app(cfg: Settings = settings, mock: bool = False) -> FastAPI:
    narrator = MockNarrator(cfg) if mock else LocalNarrator(cfg)
    if cfg.tts_backend == "piper":
        tts = PiperTTS(cfg)
    elif cfg.tts_backend == "command" and cfg.tts_command:
        tts = CommandTTS(cfg.tts_command)
    else:
        tts = StdoutTTS()
    service = VoiceService(cfg, narrator, tts, OpenCodeClient(cfg))
    app = FastAPI(title="OpenCode Live Voice", version="0.1.0")
    app.state.service = service

    @app.get("/healthz")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/v1/events", status_code=202)
    async def events(event: VoiceEvent) -> dict[str, bool]:
        await service.ingest(event)
        return {"accepted": True}

    @app.post("/v1/utterances")
    async def utterances(body: Utterance) -> dict[str, str]:
        if not body.text.strip():
            raise HTTPException(400, "empty utterance")
        result = await service.utterance(body.text, body.session_id)
        return {"intent": result.kind.value}

    @app.get("/v1/sessions/{session_id}")
    async def session(session_id: str) -> dict:
        return service.state.get(session_id).model_dump()

    return app


app = create_app()
