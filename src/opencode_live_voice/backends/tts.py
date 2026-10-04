from __future__ import annotations

import asyncio
import shlex
from dataclasses import dataclass

from ..config import Settings


class TTS:
    async def speak(self, text: str, interrupt: bool = False) -> None:
        raise NotImplementedError

    async def stop(self) -> None:
        return None


class StdoutTTS(TTS):
    async def speak(self, text: str, interrupt: bool = False) -> None:
        print(f"SPEAK: {text}", flush=True)


@dataclass
class PiperTTS(TTS):
    settings: Settings
    _proc: asyncio.subprocess.Process | None = None

    async def stop(self) -> None:
        if self._proc and self._proc.returncode is None:
            self._proc.terminate()
            try:
                await asyncio.wait_for(self._proc.wait(), timeout=0.5)
            except TimeoutError:
                self._proc.kill()

    async def speak(self, text: str, interrupt: bool = False) -> None:
        if interrupt:
            await self.stop()
        if not self.settings.piper_voice:
            raise RuntimeError("OLV_PIPER_VOICE is required for Piper")
        cmd = f"piper --model {shlex.quote(self.settings.piper_voice)} --output-raw"
        player = "aplay -r 22050 -f S16_LE -t raw -"
        shell = f"printf %s {shlex.quote(text)} | {cmd} | {player}"
        self._proc = await asyncio.create_subprocess_shell(shell)
        await self._proc.wait()


class CommandTTS(TTS):
    def __init__(self, command: str) -> None:
        self.command = command
        self._proc: asyncio.subprocess.Process | None = None

    async def stop(self) -> None:
        if self._proc and self._proc.returncode is None:
            self._proc.terminate()

    async def speak(self, text: str, interrupt: bool = False) -> None:
        if interrupt:
            await self.stop()
        argv = shlex.split(self.command) + [text]
        self._proc = await asyncio.create_subprocess_exec(*argv)
        await self._proc.wait()
