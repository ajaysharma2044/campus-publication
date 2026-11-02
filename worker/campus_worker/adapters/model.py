"""Model adapter with role routing, budget reservation, escalation ceiling and run recording.

Role alias → model id comes from config.ModelRouting (SPEC §36). Every call records the
requested and resolved model, fallback rationale, escalation level and usage in `runs`.

Providers:
- AnthropicProvider: real API, only if ANTHROPIC_API_KEY is present. Otherwise capability() is
  'unconnected' and any call raises NotConnected. Nothing here is proof of routing until a real
  call has been made with a key (SPEC §39).
- FixtureProvider: deterministic scripted responses for tests. capability() is 'fixture'.

Escalation policy (SPEC §36): one same-tier repair, then at most one escalation, only for
substantive judgment defects. Missing evidence / denied access / invalid input / outage never
escalate — they hold or retry.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Callable, Protocol
from uuid import UUID

import psycopg

from ..budget import BudgetExceeded, Unpriced, estimate_model_call_minor, reconcile, reserve
from ..config import Budget, ModelRouting
from ..types import UsageEntry
from .base import Capability, NotConnected, ProviderError


@dataclass
class ModelResponse:
    text: str
    model: str
    input_tokens: int
    output_tokens: int
    cached_tokens: int = 0
    stop_reason: str | None = None


class Provider(Protocol):
    def capability(self) -> Capability: ...
    def complete(self, *, model: str, system: str, user: str, max_tokens: int) -> ModelResponse: ...
    def available_models(self) -> set[str]: ...


class AnthropicProvider:
    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self._key = api_key if api_key is not None else os.environ.get("ANTHROPIC_API_KEY")
        self._base_url = base_url
        self._client = None

    def capability(self) -> Capability:
        if not self._key:
            return Capability("anthropic", "unconnected", "ANTHROPIC_API_KEY not set; worker model calls are impossible", priced=True)
        return Capability("anthropic", "connected", "API key present (API-billed, not subscription)", priced=True, features=("messages",))

    def available_models(self) -> set[str]:
        return set()  # unknown until a live call verifies; we never assume

    def complete(self, *, model: str, system: str, user: str, max_tokens: int) -> ModelResponse:
        if not self._key:
            raise NotConnected("anthropic")
        import anthropic  # local import so tests never need the client

        if self._client is None:
            kw = {"api_key": self._key}
            if self._base_url:
                kw["base_url"] = self._base_url
            self._client = anthropic.Anthropic(**kw)
        try:
            msg = self._client.messages.create(
                model=model, max_tokens=max_tokens, system=system,
                messages=[{"role": "user", "content": user}],
            )
        except anthropic.RateLimitError as e:  # type: ignore[attr-defined]
            raise ProviderError(str(e), retryable=True, kind="rate_limit") from e
        except anthropic.AuthenticationError as e:  # type: ignore[attr-defined]
            raise ProviderError(str(e), retryable=False, kind="auth") from e
        except anthropic.APIStatusError as e:  # type: ignore[attr-defined]
            retryable = e.status_code >= 500 or e.status_code == 529
            raise ProviderError(str(e), retryable=retryable, kind="outage" if retryable else "invalid_input") from e
        text = "".join(getattr(b, "text", "") for b in msg.content)
        u = msg.usage
        return ModelResponse(text, msg.model, u.input_tokens, u.output_tokens,
                             getattr(u, "cache_read_input_tokens", 0) or 0, msg.stop_reason)


class FixtureProvider:
    """Scripted provider for tests. `script` maps (model, tag) → text or exception, where tag is
    taken from the user prompt's first line '#tag:...' if present."""

    def __init__(self, script: dict[tuple[str, str], str | Exception] | None = None, models: set[str] | None = None):
        self.script = script or {}
        self.calls: list[dict] = []
        self.models = models or {"claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5"}

    def capability(self) -> Capability:
        return Capability("fixture", "fixture", "scripted responses for tests; not a live service", priced=False)

    def available_models(self) -> set[str]:
        return set(self.models)

    def complete(self, *, model: str, system: str, user: str, max_tokens: int) -> ModelResponse:
        tag = user.split("\n", 1)[0].removeprefix("#tag:") if user.startswith("#tag:") else "default"
        self.calls.append({"model": model, "tag": tag, "max_tokens": max_tokens})
        if model not in self.models:
            raise ProviderError(f"model {model} unavailable", retryable=False, kind="invalid_input")
        out = self.script.get((model, tag), self.script.get((model, "default"), '{"ok": true}'))
        if isinstance(out, Exception):
            raise out
        return ModelResponse(out, model, len(system) // 4 + len(user) // 4, len(out) // 4)


class HoldJob(Exception):
    """Signal to the orchestrator: hold with machine-readable reason + retry condition."""

    def __init__(self, reason: str, retry_condition: str):
        super().__init__(reason)
        self.reason = reason
        self.retry_condition = retry_condition


@dataclass
class CallOutcome:
    response: ModelResponse | None
    resolved_model: str
    requested_model: str
    escalation_level: int
    attempts: int
    fallback_rationale: str | None = None
    repairs: int = 0
    validation_errors: list[str] = field(default_factory=list)


class ModelRouter:
    def __init__(self, routing: ModelRouting, budget: Budget, provider: Provider):
        self.routing = routing
        self.budget = budget
        self.provider = provider

    def resolve(self, role: str) -> str:
        return self.routing.resolve(role)

    def _pick_available(self, model: str) -> tuple[str, str | None]:
        avail = self.provider.available_models()
        if not avail or model in avail:
            return model, None
        fb = self.routing.fallbacks.get(model)
        if fb and fb in avail:
            return fb, f"requested {model} unavailable; preapproved fallback {fb}"
        raise HoldJob("model_unavailable", f"model {model} (or preapproved fallback) becomes available")

    def call(
        self,
        conn: psycopg.Connection,
        *,
        role: str,
        system: str,
        user: str,
        max_tokens: int,
        max_input_tokens: int,
        job_id: UUID | None,
        run_id: UUID | None,
        validate: Callable[[str], list[str]] | None = None,
        allow_escalation: bool = True,
    ) -> CallOutcome:
        """Make a budgeted, routed call with bounded repair/escalation.

        validate(text) returns a list of defect strings; empty = accepted. Defects prefixed
        'judgment:' may escalate; others ('schema:', 'evidence:') get one same-tier repair and then
        hold. Raises HoldJob / BudgetExceeded / ProviderError for the orchestrator.
        """
        requested = self.resolve(role)
        model, fb_reason = self._pick_available(requested)
        level = 0
        repairs = 0
        attempts = 0
        errors: list[str] = []
        prompt_user = user
        while True:
            attempts += 1
            try:
                est = estimate_model_call_minor(model, max_input_tokens, max_tokens)
            except Unpriced as e:
                raise HoldJob("unpriced_model", f"price entry for {model} added to budget.MODEL_PRICE_PER_MTOK_MINOR") from e
            res = reserve(conn, self.budget, UsageEntry(provider="anthropic", kind="reservation", amount_minor=est,
                                                         job_id=job_id, run_id=run_id, detail={"model": model, "role": role}))
            try:
                resp = self.provider.complete(model=model, system=system, user=prompt_user, max_tokens=max_tokens)
            except ProviderError as e:
                reconcile(conn, res, 0, detail={"error": e.kind})
                if e.kind in ("auth", "usage_limit"):
                    raise HoldJob(f"provider_{e.kind}", "credential or usage allowance restored") from e
                raise  # retryable outages/rate limits go through the queue's retry path, never escalation
            actual = _actual_cost_minor(resp)
            reconcile(conn, res, actual, detail={"input": resp.input_tokens, "output": resp.output_tokens, "cached": resp.cached_tokens, "model": resp.model})
            self._record_run(conn, run_id, role, requested, resp.model, fb_reason, level, resp)
            errors = validate(resp.text) if validate else []
            if not errors:
                return CallOutcome(resp, resp.model, requested, level, attempts, fb_reason, repairs, [])
            judgment = all(e.startswith("judgment:") for e in errors)
            if repairs < self.routing.max_same_tier_repairs:
                repairs += 1
                prompt_user = user + "\n\n[REPAIR] Previous output had defects: " + "; ".join(errors)
                continue
            if judgment and allow_escalation and level < self.routing.max_escalations:
                level += 1
                esc = self.routing.escalation_model
                if esc == model:
                    raise HoldJob("escalation_exhausted", "owner review of substantive judgment defect")
                model, fb2 = self._pick_available(esc)
                fb_reason = fb2 or fb_reason
                prompt_user = user + "\n\n[ESCALATED] A prior attempt had defects: " + "; ".join(errors)
                repairs = 0  # one repair allowed at the escalated tier too, still within ceiling
                continue
            if judgment:
                raise HoldJob("escalation_exhausted", "owner review of substantive judgment defect")
            # Non-judgment defects (schema/evidence) never escalate: hold.
            if any(e.startswith("evidence:") for e in errors):
                raise HoldJob("missing_evidence", "evidence supplied; retry at same tier")
            raise HoldJob("output_invalid", "manual inspection of malformed output")

    def _record_run(self, conn, run_id, role, requested, resolved, fb_reason, level, resp: ModelResponse) -> None:
        if run_id is None:
            return
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE runs SET model_role=%s, requested_model=%s, resolved_model=%s, fallback_rationale=%s,
                   escalation_level=%s, usage = COALESCE(usage,'{}'::jsonb) || %s::jsonb WHERE id=%s""",
                (role, requested, resolved, fb_reason, level,
                 json.dumps({"input_tokens": resp.input_tokens, "output_tokens": resp.output_tokens, "cached_tokens": resp.cached_tokens, "calls": 1}),
                 run_id),
            )
        conn.commit()


def _actual_cost_minor(resp: ModelResponse) -> int:
    from ..budget import MODEL_PRICE_PER_MTOK_MINOR

    cin, cout = MODEL_PRICE_PER_MTOK_MINOR.get(resp.model, (0, 0))
    return int(((resp.input_tokens - resp.cached_tokens) * cin + resp.cached_tokens * cin * 0.1 + resp.output_tokens * cout) / 1_000_000 + 0.999)


def default_provider() -> Provider:
    return AnthropicProvider()
