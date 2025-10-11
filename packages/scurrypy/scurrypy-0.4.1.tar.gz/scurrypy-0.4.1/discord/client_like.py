from typing import Protocol

from .config import BaseConfig
from .http import HTTPClient
from .logger import Logger

class ClientLike(Protocol):
    """Exposes a common interface for [`Client`][discord.client.Client]."""
    application_id: int
    """Bot's application ID."""

    config: BaseConfig
    """User-defined config."""

    _http: HTTPClient
    """HTTP session for requests."""

    _logger: Logger
    """Logger instance to log events."""
