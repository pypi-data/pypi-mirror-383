import typing

from .base import Guard

if typing.TYPE_CHECKING:
    from hassette.events import CallServiceEvent


def home_assistant_restarted(event: "CallServiceEvent"):
    return event.payload.domain == "homeassistant" and event.payload.service == "restart"


HomeAssistantRestarted = Guard["CallServiceEvent"](home_assistant_restarted)
