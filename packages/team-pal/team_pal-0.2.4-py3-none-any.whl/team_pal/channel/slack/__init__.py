"""Slack channel adapter package."""

from .client import SlackClientError, SlackClientProtocol, SlackEvent, SlackMessage, SlackPostResponse, SlackSocketClient
from .dispatcher import DefaultSlackResponseFormatter, SlackResultDispatcher, SlackResponseFormatter
from .factory import register_slack_components
from .listener import DefaultSlackInstructionFactory, SlackInstructionFactory, SlackInstructionListener

__all__ = [
    "SlackClientError",
    "SlackClientProtocol",
    "SlackEvent",
    "SlackMessage",
    "SlackPostResponse",
    "SlackSocketClient",
    "SlackResultDispatcher",
    "SlackResponseFormatter",
    "DefaultSlackResponseFormatter",
    "register_slack_components",
    "SlackInstructionFactory",
    "DefaultSlackInstructionFactory",
    "SlackInstructionListener",
]
