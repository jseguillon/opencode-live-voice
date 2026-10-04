from opencode_live_voice.models import IntentKind
from opencode_live_voice.router import route_text


def test_critical_commands_are_deterministic():
    assert route_text("stop").kind == IntentKind.STOP
    assert route_text("allow once").kind == IntentKind.ALLOW_ONCE
    assert route_text("deny").kind == IntentKind.DENY


def test_status_is_local():
    assert route_text("what is it doing?").kind == IntentKind.STATUS


def test_new_instruction_is_forwarded():
    assert route_text("inspect the controller before editing Helm").kind == IntentKind.FORWARD_TO_OPENCODE
