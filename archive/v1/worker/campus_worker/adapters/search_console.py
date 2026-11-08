"""Google Search Console adapter (SPEC §21). Unconnected until a verified property and a service
account exist. Query rows are incomplete by design (Google omits low-volume queries), so a missing
row is never interpreted as zero demand."""
from __future__ import annotations

import os

from .base import Capability, NotConnected


class SearchConsoleAdapter:
    provider_name = "search_console"

    def __init__(self, credentials_path: str | None = None, property_url: str | None = None):
        self._creds = credentials_path or os.environ.get("CAMPUS_GSC_CREDENTIALS_PATH")
        self._property = property_url or os.environ.get("CAMPUS_GSC_PROPERTY")

    def capability(self) -> Capability:
        if self._creds and self._property and os.path.exists(self._creds):
            return Capability(self.provider_name, "connected", "service-account credentials and property configured (untested until first query)", priced=False)
        return Capability(self.provider_name, "unconnected", "no verified Search Console property / service account", priced=False)

    def query(self, *_a, **_k):
        raise NotConnected(self.provider_name)
