from __future__ import annotations

from enum import StrEnum
from typing import Any
from pydantic import BaseModel, Field


class EventKind(StrEnum):
    SESSION_STARTED = "session_started"
    COMPLETE = "complete"
    SUBAGENT_COMPLETE = "subagent_complete"
    PERMISSION = "permission"
    QUESTION = "question"
    ERROR = "error"
    USER_CANCELLED = "user_cancelled"
    TOOL_STARTED = "tool_started"
    TOOL_FINISHED = "tool_finished"
    STATUS = "status"
    MESSAGE_DELTA = "message_delta"
    TODO = "todo"


class VoiceEvent(BaseModel):
    event: EventKind
    session_id: str | None = None
    agent_name: str | None = None
    message: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp_ms: int | None = None


class SessionState(BaseModel):
    session_id: str
    goal: str | None = None
    agent_name: str | None = None
    phase: str = "unknown"
    recent_events: list[str] = Field(default_factory=list)
    last_spoken: str | None = None
    muted: bool = False


class NarrationDecision(BaseModel):
    speak: bool
    text: str = ""
    priority: str = "normal"
    interrupt: bool = False


class IntentKind(StrEnum):
    STOP = "stop"
    ALLOW_ONCE = "allow_once"
    ALLOW_ALWAYS = "allow_always"
    DENY = "deny"
    MUTE = "mute"
    UNMUTE = "unmute"
    STATUS = "status"
    REPEAT = "repeat"
    SUMMARIZE = "summarize"
    QUIETER = "quieter"
    FORWARD_TO_OPENCODE = "forward_to_opencode"


class RoutedIntent(BaseModel):
    kind: IntentKind
    text: str = ""
    session_id: str | None = None
