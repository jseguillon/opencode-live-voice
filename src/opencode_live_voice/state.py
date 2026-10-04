from __future__ import annotations

from .models import SessionState, VoiceEvent


class StateStore:
    def __init__(self, max_recent: int = 12) -> None:
        self.max_recent = max_recent
        self._states: dict[str, SessionState] = {}

    def get(self, session_id: str) -> SessionState:
        if session_id not in self._states:
            self._states[session_id] = SessionState(session_id=session_id)
        return self._states[session_id]

    def update(self, event: VoiceEvent) -> SessionState | None:
        if not event.session_id:
            return None
        state = self.get(event.session_id)
        if event.agent_name:
            state.agent_name = event.agent_name
        if event.message:
            state.recent_events.append(f"{event.event}: {event.message}")
        else:
            state.recent_events.append(str(event.event))
        state.recent_events = state.recent_events[-self.max_recent :]
        if event.event.value in {"session_started", "status"}:
            state.phase = event.message or event.event.value
        elif event.event.value in {"complete", "subagent_complete"}:
            state.phase = "complete"
        elif event.event.value == "error":
            state.phase = "error"
        elif event.event.value.startswith("tool_"):
            state.phase = "working"
        return state

    def snapshot(self) -> dict[str, SessionState]:
        return dict(self._states)
