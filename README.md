# OpenCode Live Voice

Local, low-latency voice control and narration for OpenCode.

**The coding model remains remote/paid. The voice experience is local.** The local LLM does not code; it only narrates trusted OpenCode events, answers local status questions, cleans speech text, and routes intent.

## Architecture

```text
                           OpenCode
                       paid coding LLM
                              |
             +----------------+----------------+
             |                                 |
   opencode-notifier                   opencode-live-events
 lifecycle/permission events           fine activity events
             |                                 |
             +---------------+-----------------+
                             |
                       loopback HTTP
                             |
                    local voice daemon
                    RTX 4090 / WSL2
                 +-----------+-----------+
                 |           |           |
                STT      local LLM       TTS
             whisper/    Qwen-class    Piper /
             Qwen-ASR    3B-4B         Qwen-TTS
                 |           |           |
                 +----- intent/router ---+
                             |
                 local status/control OR
                 explicit new work prompt
                             |
                           OpenCode
```

## Cost boundary

Local and free by default:
- narration of OpenCode activity
- “what is it doing?”, repeat, summarize, mute/unmute
- STT cleanup and routing
- TTS
- deterministic stop/cancel/permission-control recognition

Can invoke the paid coding model:
- explicit new coding instructions
- questions that genuinely require repository/code context

The daemon never uses the local interaction LLM as OpenCode's coding model.

## Quick start (WSL2)

Python 3.12:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
make test
make demo
```

Start the daemon:

```bash
opencode-live-voice
```

It binds to `127.0.0.1:8765` by default.

### Local interaction LLM

Point `OLV_LOCAL_LLM_BASE_URL` at any local OpenAI-compatible server. A small Qwen-class 3B/4B model is intentionally sufficient because it receives compact session state, not the whole repository.

Example:

```bash
export OLV_LOCAL_LLM_BASE_URL=http://127.0.0.1:8085/v1
export OLV_LOCAL_LLM_MODEL=qwen3.5-4b
export OLV_LOCAL_LLM_API_KEY=dummy
```

Unsloth Studio works well when exposing an OpenAI-compatible local endpoint.

## `opencode-notifier` integration

Keep `@mohak34/opencode-notifier` upstream/unmodified. Copy `examples/opencode-notifier.json` to `~/.config/opencode/opencode-notifier.json` after installing this package so the `opencode-live-voice-event` executable is on PATH.

The adapter receives `{event}`, `{sessionID}`, `{agentName}`, `{message}` and POSTs them to the local daemon. It exits quickly and does not own models.

## Fine-grained OpenCode events

`plugin/` contains the separate `opencode-live-events` plugin. It emits tool start/end, status, todo, and assistant-output-update events to the same daemon.

This split avoids forking `opencode-notifier` and keeps notification/focus/platform logic upstream.

```bash
cd plugin
npm install
npm run typecheck
```

The plugin deliberately avoids shipping raw assistant/code output in narration events by default. It sends state transitions and metadata, reducing accidental code leakage into speech.

## TTS

Default is `stdout`, useful for development and CI:

```text
SPEAK: The agent is working on the requested change.
```

Piper:

```bash
export OLV_TTS_BACKEND=piper
export OLV_PIPER_VOICE=$HOME/.local/share/piper-voices/en_US-lessac-medium.onnx
```

`command` mode can wrap Kokoro or a Qwen3-TTS local service/client:

```bash
export OLV_TTS_BACKEND=command
export OLV_TTS_COMMAND='/path/to/tts-client --endpoint http://127.0.0.1:8880'
```

The backend boundary is intentionally small so Qwen3-TTS streaming can replace Piper without coupling it to OpenCode.

## STT

The first native backend is `whisper.cpp`. Install `whisper-cli`, then:

```bash
export OLV_WHISPER_MODEL=$HOME/.local/share/whisper-cpp/ggml-large-v3-turbo-q5_0.bin
```

Qwen3-ASR and Moonshine should be integrated as local service adapters behind the same `STT` interface. Keeping STT out-of-process is recommended if it shares the 4090 with TTS and the interaction LLM.

### WSL2 audio

WSL2 typically receives microphone/audio through WSLg PulseAudio rather than `/dev/snd`. Verify `pactl info` and input sources first. Keep audio capture local to WSL/Windows; the OpenCode server may be elsewhere.

## Barge-in and controls

The routing layer treats these without an LLM:

```text
stop / cancel / annule / arrête
allow / approve / autorise
always allow / approve always
deny / reject / refuse
mute / unmute
```

`stop` first interrupts current TTS, then calls OpenCode abort.

Permission approval is intentionally incomplete until a structured pending permission ID is available. Spoken “allow” never blindly approves an unknown request, and `always` is never the default.

## Local vs paid routing

Examples handled locally:

```text
what is it doing?
repeat
summarize
mute
be quieter
```

Example forwarded to OpenCode, and therefore potentially to the paid coding model:

```text
inspect the controller before changing the Helm manifests
```

## API

```text
GET  /healthz
POST /v1/events
POST /v1/utterances
GET  /v1/sessions/{session_id}
```

Example event:

```json
{
  "event": "tool_started",
  "session_id": "ses_123",
  "message": "pytest"
}
```

Example utterance:

```json
{
  "session_id": "ses_123",
  "text": "what is it doing?"
}
```

## Demo

```bash
make demo
```

The demo uses a mock narrator and stdout TTS. It requires no GPU, microphone, OpenCode instance, external API, or secret.

## Tests

```bash
make test
make lint
make typecheck
cd plugin && npm install && npm run typecheck
```

GitHub Actions runs Python lint/tests/demo and TypeScript type checking.

## Roadmap

- streaming microphone capture + Silero VAD
- Qwen3-ASR and Moonshine service adapters
- native Qwen3-TTS streaming client
- permission-ID aware voice approval (`once`/`always`/`reject`)
- session selection when several OpenCode sessions are active
- adaptive verbosity (“be quieter” / “tell me more”)
- latency metrics from speech end -> intent -> first audio frame

## Security

- daemon binds loopback by default
- no secrets in event payloads
- no shell interpolation of notifier message fields
- local LLM cannot approve permissions
- OpenCode commands remain explicit
- voice integration failures are fail-open for coding execution, not for permissions

## License
MIT
