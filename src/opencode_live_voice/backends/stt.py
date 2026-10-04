from __future__ import annotations

import asyncio
from pathlib import Path

from ..config import Settings


class STT:
    async def transcribe(self, wav_path: str) -> str:
        raise NotImplementedError


class WhisperCppSTT(STT):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def transcribe(self, wav_path: str) -> str:
        proc = await asyncio.create_subprocess_exec(
            self.settings.whisper_cli,
            "-m", str(Path(self.settings.whisper_model).expanduser()),
            "-f", wav_path,
            "-l", "auto",
            "-nt",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        out, err = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(err.decode(errors="replace"))
        return out.decode(errors="replace").strip()
