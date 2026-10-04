from opencode_live_voice.models import EventKind, VoiceEvent
from opencode_live_voice.state import StateStore


def test_state_tracks_recent_events_and_phase():
    store = StateStore(max_recent=2)
    store.update(VoiceEvent(event=EventKind.TOOL_STARTED, session_id="s1", message="read auth.ts"))
    store.update(VoiceEvent(event=EventKind.TOOL_FINISHED, session_id="s1", message="edited auth.ts"))
    store.update(VoiceEvent(event=EventKind.COMPLETE, session_id="s1", message="done"))
    s = store.get("s1")
    assert s.phase == "complete"
    assert len(s.recent_events) == 2
