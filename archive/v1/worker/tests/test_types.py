from datetime import datetime, timezone
from uuid import uuid4
import pytest
from pydantic import ValidationError
from campus_worker.types import ClaimRecord, InstitutionRecord, SchoolConfigRecord


def _claim(**kw):
    base = dict(institution_id=uuid4(), topic_id=uuid4(), field="rate.double", value_type="money", value_number=1234500,
                unit="minor_units", currency="USD", billing_period="per_academic_year", price_basis="per_person",
                evidence_category="verified_fact", extraction_method="deterministic",
                retrieved_at=datetime.now(timezone.utc))
    base.update(kw)
    return ClaimRecord(**base)


def test_money_requires_integer_minor_units():
    with pytest.raises(ValidationError):
        _claim(value_number=1234.5)


def test_money_requires_explicit_period_and_basis():
    with pytest.raises(ValidationError):
        _claim(billing_period=None)
    with pytest.raises(ValidationError):
        _claim(price_basis=None)
    assert _claim(billing_period="unknown", price_basis="unknown").price_basis == "unknown"


def test_naive_timestamp_rejected():
    with pytest.raises(ValidationError):
        _claim(retrieved_at=datetime(2026, 1, 1))


def test_model_verified_fact_needs_confidence():
    with pytest.raises(ValidationError):
        _claim(extraction_method="model", extraction_model="claude-sonnet-5-5")
    assert _claim(extraction_method="model", extraction_model="claude-sonnet-5-5", extraction_confidence=0.9)


def test_system_type_consistency():
    with pytest.raises(ValidationError):
        InstitutionRecord(canonical_name="X System", slug="x", institution_type="university", is_system=True)


def test_unknown_audience_rejected():
    with pytest.raises(ValidationError):
        SchoolConfigRecord(audiences=["freshman_bros"])
