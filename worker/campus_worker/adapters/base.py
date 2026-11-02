from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

ConnectionState = Literal["connected", "unconnected", "disabled", "fixture"]


@dataclass(frozen=True)
class Capability:
    provider: str
    state: ConnectionState
    reason: str
    priced: bool = False
    features: tuple[str, ...] = field(default_factory=tuple)

    @property
    def connected(self) -> bool:
        return self.state == "connected"

    def as_dict(self) -> dict:
        return {
            "provider": self.provider,
            "state": self.state,
            "reason": self.reason,
            "priced": self.priced,
            "features": list(self.features),
        }


class ProviderError(Exception):
    """Base for adapter failures. `retryable` distinguishes outages/rate limits from permanent
    errors (invalid input, authorization)."""

    def __init__(self, message: str, *, retryable: bool, retry_after_seconds: int | None = None, kind: str = "error"):
        super().__init__(message)
        self.retryable = retryable
        self.retry_after_seconds = retry_after_seconds
        self.kind = kind  # 'rate_limit' | 'outage' | 'auth' | 'invalid_input' | 'usage_limit' | 'error'


class NotConnected(ProviderError):
    def __init__(self, provider: str):
        super().__init__(f"{provider} adapter is unconnected (no credential)", retryable=False, kind="auth")
