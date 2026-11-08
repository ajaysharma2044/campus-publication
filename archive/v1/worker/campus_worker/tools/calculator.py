"""Total-cost calculator (SPEC §19).

Inputs are typed line items with explicit billing period, basis, and whether they are mandatory,
refundable, or user assumptions. Output normalises every item to one comparison period and
reports: mandatory total, optional total, refundable deposits (shown separately, never added to
cost), unknown items (listed, never zeroed), and assumption items (labelled).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Period = Literal["per_month", "per_semester", "per_academic_year", "per_term", "per_year", "one_time", "per_week", "per_day", "unknown"]
Basis = Literal["per_person", "per_unit", "per_bed", "unknown"]

# Conversions to an academic year under an explicit assumption set. The reader can change these.
DEFAULT_ASSUMPTIONS = {"months_in_academic_year": 9, "semesters_in_academic_year": 2, "terms_in_academic_year": 2, "weeks_in_academic_year": 36,
                       "days_in_academic_year": 270, "occupants_per_unit": None}


@dataclass
class LineItem:
    label: str
    amount_minor: int | None             # None = unknown
    period: Period
    basis: Basis = "per_person"
    mandatory: bool = True
    refundable_deposit: bool = False
    is_assumption: bool = False          # entered by the reader, not a published fact
    claim_id: str | None = None
    note: str | None = None


@dataclass
class Normalized:
    label: str
    amount_minor: int | None
    source_period: Period
    status: str                          # 'included' | 'unknown' | 'deposit' | 'optional' | 'assumption' | 'not_convertible'
    note: str | None = None
    claim_id: str | None = None


@dataclass
class CalcResult:
    target_period: Period
    mandatory_total_minor: int
    optional_total_minor: int
    deposits_minor: int
    items: list[Normalized]
    unknown_items: list[str]
    assumptions_used: dict
    exclusions: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def complete(self) -> bool:
        return not self.unknown_items and not self.errors


def _to_academic_year(amount: int, period: Period, a: dict) -> int | None:
    if period == "per_academic_year":
        return amount
    if period == "per_year":
        return amount  # treated as the same 12-month obligation; disclosed in exclusions
    if period == "per_semester":
        return amount * a["semesters_in_academic_year"]
    if period == "per_term":
        return amount * a["terms_in_academic_year"]
    if period == "per_month":
        return amount * a["months_in_academic_year"]
    if period == "per_week":
        return amount * a["weeks_in_academic_year"]
    if period == "per_day":
        return amount * a["days_in_academic_year"]
    if period == "one_time":
        return amount
    return None


def _from_academic_year(amount_ay: int, target: Period, a: dict) -> int | None:
    div = {"per_academic_year": 1, "per_year": 1, "per_semester": a["semesters_in_academic_year"], "per_term": a["terms_in_academic_year"],
           "per_month": a["months_in_academic_year"]}.get(target)
    if div is None:
        return None
    return round(amount_ay / div)


def normalize_basis(item: LineItem, assumptions: dict) -> tuple[int | None, str | None]:
    """Convert per-unit amounts to per-person only when occupants_per_unit is an explicit assumption."""
    if item.amount_minor is None:
        return None, None
    if item.basis == "per_unit":
        occ = assumptions.get("occupants_per_unit")
        if not occ:
            return None, "per-unit price; enter occupants per unit to compare per person"
        return round(item.amount_minor / occ), f"per-unit price divided by {occ} occupants (your assumption)"
    if item.basis == "unknown":
        return None, "price basis not stated by the source"
    return item.amount_minor, None


def calculate(items: list[LineItem], *, target_period: Period = "per_academic_year", assumptions: dict | None = None) -> CalcResult:
    a = dict(DEFAULT_ASSUMPTIONS, **(assumptions or {}))
    out = CalcResult(target_period, 0, 0, 0, [], [], a)
    if target_period not in ("per_academic_year", "per_semester", "per_month", "per_term", "per_year"):
        out.errors.append(f"unsupported comparison period {target_period}")
        return out
    for it in items:
        if it.amount_minor is None:
            out.items.append(Normalized(it.label, None, it.period, "unknown", it.note or "amount unknown; not included in totals", it.claim_id))
            out.unknown_items.append(it.label)
            continue
        if it.amount_minor < 0:
            out.errors.append(f"{it.label}: negative amount")
            continue
        per_person, basis_note = normalize_basis(it, a)
        if per_person is None:
            out.items.append(Normalized(it.label, None, it.period, "unknown", basis_note, it.claim_id))
            out.unknown_items.append(it.label)
            continue
        if it.refundable_deposit:
            out.deposits_minor += per_person
            out.items.append(Normalized(it.label, per_person, it.period, "deposit", "refundable deposit; shown separately, not a cost", it.claim_id))
            continue
        if it.period == "unknown":
            out.items.append(Normalized(it.label, per_person, it.period, "not_convertible", "billing period not stated; cannot convert", it.claim_id))
            out.unknown_items.append(it.label)
            continue
        ay = _to_academic_year(per_person, it.period, a)
        if ay is None:
            out.items.append(Normalized(it.label, per_person, it.period, "not_convertible", "cannot convert this period", it.claim_id))
            out.unknown_items.append(it.label)
            continue
        if it.period == "one_time" and target_period != "per_academic_year":
            out.exclusions.append(f"{it.label} is a one-time charge; counted once in the {target_period.replace('_', ' ')} figure")
        if it.period == "per_year":
            out.exclusions.append(f"{it.label} is billed per 12-month year; shown against an academic-year basis")
        converted = _from_academic_year(ay, target_period, a) if it.period != "one_time" else per_person
        status = "assumption" if it.is_assumption else ("included" if it.mandatory else "optional")
        if it.mandatory:
            out.mandatory_total_minor += converted
        else:
            out.optional_total_minor += converted
        note = basis_note or ("your assumption, not a published figure" if it.is_assumption else None)
        out.items.append(Normalized(it.label, converted, it.period, status, note, it.claim_id))
    return out
