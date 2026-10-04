from fastapi.testclient import TestClient
from opencode_live_voice.api import create_app
from opencode_live_voice.config import Settings


def test_health_and_event_acceptance():
    app = create_app(Settings(), mock=True)
    c = TestClient(app)
    assert c.get("/healthz").json() == {"status": "ok"}
    r = c.post("/v1/events", json={"event": "session_started", "session_id": "s1", "message": "starting"})
    assert r.status_code == 202


def test_status_utterance_stays_local(monkeypatch):
    app = create_app(Settings(), mock=True)
    c = TestClient(app)
    r = c.post("/v1/utterances", json={"session_id": "s1", "text": "what is it doing?"})
    assert r.status_code == 200
    assert r.json()["intent"] == "status"
