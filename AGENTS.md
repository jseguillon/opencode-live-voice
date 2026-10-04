# AGENTS.md

## Design boundary
The paid/remote OpenCode coding model and the local voice interaction model are separate trust/cost domains.
Never route local status, narration, mute/repeat/status requests to the paid coding model.
Only explicit new work instructions or code-context questions may be forwarded to OpenCode.

## Safety
- Critical controls (`stop`, `cancel`, `allow once`, `allow always`, `deny`, `mute`, `unmute`) must be deterministic.
- Never let an LLM infer permission approval.
- Never default permission approval to `always`.
- Voice failures must never block OpenCode execution.
- Bind daemon APIs to loopback by default.

## Development
- Keep backends behind small interfaces.
- CI must run without GPU, microphone, TTS hardware, paid APIs, or secrets.
- Prefer structured events over parsing terminal text.
- Do not claim unsupported OpenCode resume/checkpoint semantics.
- Add tests for routing/state/coalescing for every behavior change.
