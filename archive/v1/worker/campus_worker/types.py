"""Typed records shared by the worker (pydantic v2). Mirrors migration 0001 column semantics.

These are validation boundaries for data entering the database and for role outputs, not ORM
models. Money is always integer minor units with an explicit currency.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

InstitutionType = Literal[
    "university", "college", "community_college", "technical_college", "graduate_school", "system", "other"
]
Control = Literal["public", "private_nonprofit", "private_forprofit", "unknown"]
IdentityStatus = Literal["verified", "pending_verification", "synthetic_fixture", "merged", "closed"]
EvidenceCategory = Literal[
    "verified_fact", "estimate", "attributed_experience", "unknown", "not_applicable", "stale", "conflicted"
]
BillingPeriod = Literal[
    "per_month", "per_semester", "per_academic_year", "per_term", "per_year", "one_time", "per_week", "per_day", "unknown"
]
PriceBasis = Literal["per_person", "per_unit", "per_bed", "unknown"]
Applicability = Literal["applicable", "not_applicable", "unknown"]
JobState = Literal["queued", "leased", "succeeded", "retry_wait", "held", "dead_letter", "cancelled"]
Decision = Literal["advance", "update", "merge", "watch", "reject", "hold"]

AUDIENCES = (
    "first_year",
    "transfer",
    "returning_undergraduate",
    "graduate",
    "community_college_student",
    "commuter",
    "adult_learner",
    "international",
    "parent",
)


class InstitutionRecord(BaseModel):
    canonical_name: str = Field(min_length=2)
    slug: str = Field(pattern=r"^[a-z0-9][a-z0-9-]*$")
    institution_type: InstitutionType
    control: Control = "unknown"
    is_system: bool = False
    country_code: str = "US"
    state_code: str | None = None
    city: str | None = None
    primary_domain: str | None = None
    identity_status: IdentityStatus = "pending_verification"
    external_ids: dict[str, str] = Field(default_factory=dict)  # system_name -> external_id
    aliases: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _system_type_consistency(self):
        if self.is_system and self.institution_type != "system":
            raise ValueError("is_system requires institution_type='system'")
        return self


class CampusRecord(BaseModel):
    name: str
    slug: str = Field(pattern=r"^[a-z0-9][a-z0-9-]*$")
    is_main: bool = False
    city: str | None = None
    state_code: str | None = None
    timezone: str = "America/New_York"
    status: Literal["active", "closed", "merged", "synthetic_fixture"] = "active"


class SchoolConfigRecord(BaseModel):
    locale: str = "en-US"
    timezone: str = "America/New_York"
    academic_calendar: Literal["semester", "quarter", "trimester", "rolling", "mixed", "unknown"] = "unknown"
    source_domains: list[str] = Field(default_factory=list)
    permitted_connectors: list[str] = Field(default_factory=list)
    audiences: list[str] = Field(default_factory=list)
    coverage_status: Literal["registry_only", "onboarding", "pilot", "active", "paused"] = "registry_only"
    is_underserved: bool = False
    topic_applicability: dict[str, Applicability] = Field(default_factory=dict)  # topic key -> state
    topic_rationale: dict[str, str] = Field(default_factory=dict)
    refresh_policy: dict = Field(default_factory=dict)

    @field_validator("audiences")
    @classmethod
    def _known_audiences(cls, v):
        bad = [a for a in v if a not in AUDIENCES]
        if bad:
            raise ValueError(f"unknown audiences: {bad}")
        return v


class ClaimRecord(BaseModel):
    institution_id: UUID
    campus_id: UUID | None = None
    entity_id: UUID | None = None
    topic_id: UUID
    field: str = Field(min_length=1)
    value_type: Literal["money", "integer", "decimal", "boolean", "text", "date", "enum", "range_money", "duration"]
    value_text: str | None = None
    value_number: int | float | None = None
    value_number_high: int | float | None = None
    value_bool: bool | None = None
    value_date: date | None = None
    unit: str | None = None
    currency: str | None = None
    billing_period: BillingPeriod | None = None
    price_basis: PriceBasis | None = None
    room_type: str | None = None
    audience_applicability: list[str] = Field(default_factory=list)
    academic_year: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}$")
    term: str | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    evidence_category: EvidenceCategory
    is_critical: bool = False
    extraction_method: Literal["deterministic", "model", "manual", "import"]
    extraction_model: str | None = None
    extraction_confidence: float | None = Field(default=None, ge=0, le=1)
    retrieved_at: datetime
    verification_due_at: datetime | None = None

    @model_validator(mode="after")
    def _money_rules(self):
        if self.value_type in ("money", "range_money"):
            if self.currency is None or self.unit != "minor_units":
                raise ValueError("money claims need currency and unit='minor_units'")
            if self.value_number is None or int(self.value_number) != self.value_number:
                raise ValueError("money must be integer minor units")
            if self.billing_period is None or self.price_basis is None:
                raise ValueError("money claims must state billing_period and price_basis (use 'unknown' explicitly)")
        if self.retrieved_at.tzinfo is None:
            raise ValueError("retrieved_at must be timezone-aware UTC")
        if self.evidence_category == "verified_fact" and self.extraction_method == "model" and (
            self.extraction_confidence is None
        ):
            raise ValueError("model-extracted verified facts must carry extraction_confidence")
        return self


class JobRecord(BaseModel):
    job_type: str
    idempotency_key: str = Field(min_length=4)
    institution_id: UUID | None = None
    campus_id: UUID | None = None
    payload: dict = Field(default_factory=dict)
    priority: int = 50
    depends_on: list[UUID] = Field(default_factory=list)
    is_paid: bool = False
    estimated_cost_minor: int | None = None
    model_role: str | None = None
    max_attempts: int = 3
    parent_job_id: UUID | None = None
    delegation_depth: int = 0


class UsageEntry(BaseModel):
    provider: str
    kind: Literal["reservation", "actual", "release", "adjustment"]
    amount_minor: int
    currency: str = "USD"
    priced: bool = True
    job_id: UUID | None = None
    run_id: UUID | None = None
    detail: dict = Field(default_factory=dict)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)
