"""Ad provider adapter (SPEC §22). AdSense is prepared but DISABLED until the owner's approved
account and publisher id exist and the environment is production. Rendering code asks
`slots_for(template)` and `loader_tag()`; both return nothing when disabled, so no ad code is
emitted. Staging can never emit production ads.
"""
from __future__ import annotations

from dataclasses import dataclass
import re

from .base import Capability

PUB_ID_RE = re.compile(r"^pub-\d{16}$")

# Conservative initial placements per template (SPEC §22). Tool controls/results never carry ads.
APPROVED_PLACEMENTS: dict[str, list[str]] = {
    "guide": ["after_essentials", "between_sections"],
    "entity_profile": ["after_facts", "desktop_sidebar"],
    "topic_hub": ["between_groups"],
    "school_hub": ["between_groups"],
    "comparison": ["after_results"],      # below the comparison table, never inside
    "tool": [],                           # no ads around calculator inputs/results in v1
    "home": [],
    "policy": [],
    "explainer": ["after_essentials"],
}


@dataclass(frozen=True)
class AdSlot:
    placement: str
    sizes: tuple[str, ...]
    lazy: bool = True


class AdSenseAdapter:
    provider_name = "adsense"

    def __init__(self, *, publisher_id: str | None, enabled: bool, environment: str, consent_required: bool = True):
        self.publisher_id = publisher_id
        self.environment = environment
        self.consent_required = consent_required
        # enabled only if all of: flag on, valid publisher id, production environment
        self.enabled = bool(enabled and publisher_id and PUB_ID_RE.match(publisher_id) and environment == "production")

    @classmethod
    def from_settings(cls, settings) -> "AdSenseAdapter":
        return cls(publisher_id=settings.adsense_publisher_id, enabled=settings.ads_enabled, environment=settings.environment)

    def capability(self) -> Capability:
        if self.enabled:
            return Capability(self.provider_name, "connected", "publisher id configured in production; approval status must be verified in the AdSense account", priced=False)
        if self.environment != "production":
            return Capability(self.provider_name, "disabled", f"ads never emitted outside production (environment={self.environment})")
        if not self.publisher_id:
            return Capability(self.provider_name, "disabled", "no AdSense publisher id; account approval is an owner dependency")
        return Capability(self.provider_name, "disabled", "ads flag off or publisher id invalid")

    def loader_tag(self, consent_granted: bool) -> str:
        """Exactly one loader, only when enabled and consent (if required) is granted."""
        if not self.enabled or (self.consent_required and not consent_granted):
            return ""
        return (f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-{self.publisher_id}" '
                f'crossorigin="anonymous"></script>')

    def slots_for(self, template: str, *, content_sections: int = 0, is_desktop: bool = False) -> list[AdSlot]:
        if not self.enabled:
            return []
        slots = []
        for placement in APPROVED_PLACEMENTS.get(template, []):
            if placement == "between_sections" and content_sections < 4:
                continue  # only justified in long guides
            if placement == "desktop_sidebar" and not is_desktop:
                continue
            slots.append(AdSlot(placement, ("responsive",)))
        return slots

    def slot_html(self, slot: AdSlot, slot_id: str) -> str:
        if not self.enabled:
            return ""
        return (f'<div class="ad-slot ad-slot--{slot.placement}" data-ad-placement="{slot.placement}" aria-label="Advertisement">'
                f'<span class="ad-slot__label">Advertisement</span>'
                f'<ins class="adsbygoogle" style="display:block" data-ad-client="ca-{self.publisher_id}" data-ad-slot="{slot_id}" '
                f'data-ad-format="auto" data-full-width-responsive="true"></ins></div>')

    def ads_txt(self) -> str:
        if not self.publisher_id:
            return "# ads.txt not generated: no publisher id\n"
        return f"google.com, {self.publisher_id}, DIRECT, f08c47fec0942fa0\n"
