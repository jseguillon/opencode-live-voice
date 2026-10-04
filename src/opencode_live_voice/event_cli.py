from __future__ import annotations

import argparse
import httpx


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("event")
    p.add_argument("session_id", nargs="?", default="")
    p.add_argument("agent_name", nargs="?", default="")
    p.add_argument("message", nargs="?", default="")
    p.add_argument("--url", default="http://127.0.0.1:8765/v1/events")
    a = p.parse_args()
    payload = {
        "event": a.event,
        "session_id": a.session_id or None,
        "agent_name": a.agent_name or None,
        "message": a.message,
    }
    with httpx.Client(timeout=0.5) as c:
        c.post(a.url, json=payload).raise_for_status()


if __name__ == "__main__":
    main()
