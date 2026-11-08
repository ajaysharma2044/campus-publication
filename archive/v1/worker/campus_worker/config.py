"""Runtime configuration. Reads environment only; never logs secret values.

Role model aliases are configured here (SPEC §36). Resolved model IDs are recorded per task in
the runs table by the model adapter. Defaults name the current Claude 5 family; they are
hypotheses to benchmark, not conclusions.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES_DIR = REPO_ROOT / "fixtures" / "synthetic"


def _env(name: str, default: str | None = None) -> str | None:
    v = os.environ.get(name)
    return v if v not in (None, "") else default


def _env_int(name: str, default: int) -> int:
    v = _env(name)
    return int(v) if v is not None else default


@dataclass(frozen=True)
class ModelRouting:
    """Role alias → provider model id. Overridable via CAMPUS_MODEL_<ROLE> env vars."""

    coordinator_model: str = "claude-sonnet-5-5"
    classification_model: str = "claude-haiku-5-5"
    extraction_model: str = "claude-sonnet-5-5"
    writing_model: str = "claude-sonnet-5-5"
    editorial_model: str = "claude-opus-5-5"
    verification_model: str = "claude-sonnet-5-5"
    escalation_model: str = "claude-opus-5-5"
    # Preapproved fallbacks (SPEC §36). A missing entry means: hold the job.
    fallbacks: dict[str, str] = field(
        default_factory=lambda: {
            "claude-haiku-5-5": "claude-sonnet-5-5",
            "claude-sonnet-5-5": "claude-opus-5-5",
        }
    )
    # Escalation ceiling: one same-tier repair, then at most one escalation.
    max_same_tier_repairs: int = 1
    max_escalations: int = 1

    @classmethod
    def from_env(cls) -> "ModelRouting":
        kw = {}
        for role in (
            "coordinator_model",
            "classification_model",
            "extraction_model",
            "writing_model",
            "editorial_model",
            "verification_model",
            "escalation_model",
        ):
            v = _env("CAMPUS_MODEL_" + role.upper())
            if v:
                kw[role] = v
        return cls(**kw)

    def resolve(self, role: str) -> str:
        if not hasattr(self, role):
            raise KeyError(f"unknown model role alias: {role}")
        return getattr(self, role)


@dataclass(frozen=True)
class Budget:
    daily_cap_minor: int = 300  # $3.00 in cents (SPEC §26)
    monthly_cap_minor: int = 6000  # $60.00
    currency: str = "USD"
    headroom_pct: int = 10  # keep this % of the cap unreserved for bounded variation

    @classmethod
    def from_env(cls) -> "Budget":
        return cls(
            daily_cap_minor=_env_int("CAMPUS_BUDGET_DAILY_MINOR", 300),
            monthly_cap_minor=_env_int("CAMPUS_BUDGET_MONTHLY_MINOR", 6000),
            headroom_pct=_env_int("CAMPUS_BUDGET_HEADROOM_PCT", 10),
        )


@dataclass(frozen=True)
class Quotas:
    """Production is unthrottled (continuous-local-run R8). Only going live is paced, by `live_ramp`.

    `live_ramp` format: comma-separated stages "<per_day>x<days>", the last stage may omit "x<days>"
    and then runs forever. Default "5x14,15" = 5 pages/day for 14 days, then 15/day. The default
    literal is guard-protected (.claude/hooks/guard.py); change it only via CAMPUS_LIVE_RAMP in .env.
    `new_pages_per_day` / `verified_updates_per_day` remain for the API-mode worker (SPEC §26) and are
    not applied to local/staging publishing.
    """

    new_pages_per_day: int = 1
    verified_updates_per_day: int = 5
    max_concurrent_model_tasks: int = 2
    max_delegation_depth: int = 1
    exploration_share_pct: int = 20  # share of discovery/research jobs reserved for underserved institutions
    live_ramp: str = "5x14,15"
    parallel_readonly_agents: int = 4  # owner override of SPEC §37 for coordinator subagents (read-only only)
    lane_mix: str = "50,30,20"  # production, discovery, maintenance (R24)
    serp_cache_days: int = 14  # R26

    @classmethod
    def from_env(cls) -> "Quotas":
        return cls(
            new_pages_per_day=_env_int("CAMPUS_QUOTA_NEW_PAGES_PER_DAY", 1),
            verified_updates_per_day=_env_int("CAMPUS_QUOTA_UPDATES_PER_DAY", 5),
            max_concurrent_model_tasks=_env_int("CAMPUS_MAX_CONCURRENT_MODEL_TASKS", 2),
            max_delegation_depth=_env_int("CAMPUS_MAX_DELEGATION_DEPTH", 1),
            exploration_share_pct=_env_int("CAMPUS_EXPLORATION_SHARE_PCT", 20),
            live_ramp=_env("CAMPUS_LIVE_RAMP", "5x14,15") or "5x14,15",
            parallel_readonly_agents=_env_int("CAMPUS_PARALLEL_READONLY_AGENTS", 4),
            lane_mix=_env("CAMPUS_LANE_MIX", "50,30,20") or "50,30,20",
            serp_cache_days=_env_int("CAMPUS_SERP_CACHE_DAYS", 14),
        )


@dataclass(frozen=True)
class Settings:
    database_url: str
    environment: str  # "development" | "staging" | "production"
    publication_name: str
    model_routing: ModelRouting
    budget: Budget
    quotas: Quotas
    ads_enabled: bool
    analytics_enabled: bool
    auto_publish_enabled: bool
    wp_base_url: str | None
    wp_user: str | None
    adsense_publisher_id: str | None
    anthropic_api_key_present: bool
    anthropic_base_url: str | None
    execution_mode: str = "session"  # session | api (continuous-local-run R7)
    live_domain: str | None = None  # CAMPUS_LIVE_DOMAIN: set only once a public domain exists (R8)

    @property
    def is_live(self) -> bool:
        """A live domain exists and this is the production environment: ready pages go live under the ramp."""
        return bool(self.live_domain) and self.environment == "production"

    @classmethod
    def from_env(cls) -> "Settings":
        env = _env("CAMPUS_ENV", "development")
        mode = (_env("CAMPUS_EXECUTION_MODE", "session") or "session").lower()
        if mode not in ("session", "api"):
            raise ValueError("CAMPUS_EXECUTION_MODE must be 'session' or 'api'")
        return cls(
            database_url=_env(
                "DATABASE_URL",
                "postgresql://campus:campus_local_dev@localhost:5432/campus_research",
            ),
            environment=env,
            publication_name=_env("CAMPUS_PUBLICATION_NAME", "Footnote Daily"),
            model_routing=ModelRouting.from_env(),
            budget=Budget.from_env(),
            quotas=Quotas.from_env(),
            ads_enabled=_env("CAMPUS_ADS_ENABLED", "false").lower() == "true" and env == "production",
            analytics_enabled=_env("CAMPUS_ANALYTICS_ENABLED", "false").lower() == "true",
            auto_publish_enabled=_env("CAMPUS_AUTO_PUBLISH_ENABLED", "false").lower() == "true",
            wp_base_url=_env("CAMPUS_WP_BASE_URL"),
            wp_user=_env("CAMPUS_WP_USER"),
            adsense_publisher_id=_env("CAMPUS_ADSENSE_PUBLISHER_ID"),
            anthropic_api_key_present=bool(_env("ANTHROPIC_API_KEY")),
            anthropic_base_url=_env("ANTHROPIC_BASE_URL"),
            execution_mode=mode,
            live_domain=_env("CAMPUS_LIVE_DOMAIN"),
        )

    def auth_mode(self) -> dict:
        """Describe how model calls would be billed, without exposing secrets (SPEC §38)."""
        if self.execution_mode == "session":
            return {
                "mode": "session",
                "billing": "language judgment runs inside the Claude Code session on the subscription; dollar caps do not apply",
                "connected": True,
                "note": "continuous-local-run R7: the ledger records unpriced usage per iteration and per agent dispatch",
            }
        if self.anthropic_api_key_present:
            return {
                "mode": "api_key",
                "billing": "API-billed per token; NOT subscription allowance",
                "connected": True,
            }
        return {
            "mode": "none",
            "billing": "no worker model credential; model adapter is unconnected",
            "connected": False,
            "note": "Claude Code's own session auth is not available to the worker and is not API billing.",
        }


def get_settings() -> Settings:
    return Settings.from_env()
