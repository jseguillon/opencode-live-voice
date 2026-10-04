from __future__ import annotations

import re

from .models import IntentKind, RoutedIntent


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9à-ÿ ]+", " ", text.casefold()).strip()


def route_deterministic(text: str, session_id: str | None = None) -> RoutedIntent | None:
    n = _norm(text)
    exact: dict[str, IntentKind] = {
        "stop": IntentKind.STOP,
        "cancel": IntentKind.STOP,
        "annule": IntentKind.STOP,
        "arrête": IntentKind.STOP,
        "arrete": IntentKind.STOP,
        "allow": IntentKind.ALLOW_ONCE,
        "approve": IntentKind.ALLOW_ONCE,
        "autorise": IntentKind.ALLOW_ONCE,
        "allow once": IntentKind.ALLOW_ONCE,
        "approve once": IntentKind.ALLOW_ONCE,
        "always allow": IntentKind.ALLOW_ALWAYS,
        "approve always": IntentKind.ALLOW_ALWAYS,
        "deny": IntentKind.DENY,
        "reject": IntentKind.DENY,
        "refuse": IntentKind.DENY,
        "mute": IntentKind.MUTE,
        "tais toi": IntentKind.MUTE,
        "unmute": IntentKind.UNMUTE,
        "parle": IntentKind.UNMUTE,
        "repeat": IntentKind.REPEAT,
        "répète": IntentKind.REPEAT,
        "repete": IntentKind.REPEAT,
        "summarize": IntentKind.SUMMARIZE,
        "résume": IntentKind.SUMMARIZE,
        "resume": IntentKind.SUMMARIZE,
        "quieter": IntentKind.QUIETER,
        "be quieter": IntentKind.QUIETER,
        "parle moins": IntentKind.QUIETER,
    }
    if n in exact:
        return RoutedIntent(kind=exact[n], text=text, session_id=session_id)
    status_patterns = (
        "what is it doing", "what s it doing", "what is he doing", "what s happening",
        "status", "where are we", "qu est ce qu il fait", "que fait il", "où en est",
        "ou en est", "ça fait quoi", "ca fait quoi",
    )
    if any(p in n for p in status_patterns):
        return RoutedIntent(kind=IntentKind.STATUS, text=text, session_id=session_id)
    return None


def route_text(text: str, session_id: str | None = None) -> RoutedIntent:
    deterministic = route_deterministic(text, session_id)
    if deterministic:
        return deterministic
    return RoutedIntent(kind=IntentKind.FORWARD_TO_OPENCODE, text=text, session_id=session_id)
