"""Side-by-side comparison (SPEC §19). Compares two or more entities field by field from shared
claim records, on an equivalent billing period/basis, with explicit unknowns and no invented
winner. Unknown is never treated as absent."""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

import psycopg

from .calculator import LineItem, calculate

COMPARE_FIELDS = [
    ("rate.room", "Room rate", "money"),
    ("amenity.air_conditioning", "Air conditioning", "boolean"),
    ("amenity.kitchen", "Kitchen access", "boolean"),
    ("amenity.laundry_in_building", "Laundry in building", "boolean"),
    ("eligibility.audience", "Who can live here", "text"),
    ("location.distance_note", "Distance to central campus", "text"),
    ("contract.length", "Contract length", "text"),
]


@dataclass
class Cell:
    display: str
    status: str                 # 'verified' | 'estimate' | 'unknown' | 'not_applicable' | 'stale' | 'conflicted'
    claim_id: str | None = None
    raw: object = None


@dataclass
class Row:
    field: str
    label: str
    cells: list[Cell]
    differs: bool


@dataclass
class Comparison:
    entities: list[dict]
    rows: list[Row]
    period: str
    basis: str
    room_type: str | None
    notes: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)

    @property
    def claim_ids(self) -> list[str]:
        return [c.claim_id for r in self.rows for c in r.cells if c.claim_id]


def _display_bool(v):
    return {True: "Yes", False: "No"}.get(v, "Unknown")


def _pick_rate(claims: list[dict], *, room_type: str | None, academic_year: str | None) -> dict | None:
    rates = [c for c in claims if c["field"] == "rate.room" and c["superseded_by_id"] is None]
    if room_type:
        rates = [c for c in rates if (c["room_type"] or "").lower() == room_type.lower()]
    if academic_year:
        rates = [c for c in rates if c["academic_year"] == academic_year]
    rates.sort(key=lambda c: (c["academic_year"] or ""), reverse=True)
    return rates[0] if rates else None


def compare(conn: psycopg.Connection, entity_ids: list[UUID], *, room_type: str | None = "double", academic_year: str | None = None,
            target_period: str = "per_academic_year") -> Comparison:
    if len(entity_ids) < 2:
        raise ValueError("comparison needs at least two entities")
    with conn.cursor() as cur:
        cur.execute("SELECT e.id, e.name, e.slug, e.institution_id, i.canonical_name FROM entities e JOIN institutions i ON i.id=e.institution_id WHERE e.id = ANY(%s)", (entity_ids,))
        ents = {r["id"]: dict(r) for r in cur.fetchall()}
        cur.execute("SELECT * FROM claims WHERE entity_id = ANY(%s) AND superseded_by_id IS NULL", (entity_ids,))
        all_claims = cur.fetchall()
    missing = [str(e) for e in entity_ids if e not in ents]
    ordered = [ents[e] for e in entity_ids if e in ents]
    by_ent: dict[UUID, list[dict]] = {e["id"]: [] for e in ordered}
    for c in all_claims:
        by_ent[c["entity_id"]].append(c)
    comp = Comparison(entities=[{"id": str(e["id"]), "name": e["name"], "slug": e["slug"], "institution": e["canonical_name"], "institution_id": str(e["institution_id"])} for e in ordered],
                      rows=[], period=target_period, basis="per_person", room_type=room_type, missing=missing)
    if len({e["institution_id"] for e in ordered}) > 1:
        comp.notes.append("Cross-school comparison: each column uses that school's own scoped records.")
    for field_key, label, kind in COMPARE_FIELDS:
        cells: list[Cell] = []
        for e in ordered:
            claims = by_ent[e["id"]]
            if kind == "money":
                c = _pick_rate(claims, room_type=room_type, academic_year=academic_year)
                if c is None:
                    cells.append(Cell("Unknown", "unknown"))
                    continue
                res = calculate([LineItem(label, int(c["value_number"]), c["billing_period"] or "unknown", c["price_basis"] or "unknown", claim_id=str(c["id"]))],
                                target_period=target_period)
                item = res.items[0]
                if item.amount_minor is None:
                    cells.append(Cell(f"Stated: ${int(c['value_number']) / 100:,.0f} ({(c['billing_period'] or 'period unknown').replace('_', ' ')}, {(c['price_basis'] or 'basis unknown').replace('_', ' ')}) — not convertible", "estimate", str(c["id"])))
                else:
                    status = "verified" if c["evidence_category"] == "verified_fact" else c["evidence_category"]
                    cells.append(Cell(f"${item.amount_minor / 100:,.0f} {target_period.replace('_', ' ')}, per person" + (f" ({c['academic_year']})" if c["academic_year"] else " (year not stated)"),
                                      status if status in ("verified", "estimate", "stale", "conflicted") else "estimate", str(c["id"]), item.amount_minor))
            else:
                c = next((x for x in claims if x["field"] == field_key), None)
                if c is None:
                    cells.append(Cell("Unknown", "unknown"))
                elif c["evidence_category"] == "not_applicable":
                    cells.append(Cell("Not applicable", "not_applicable", str(c["id"])))
                else:
                    disp = _display_bool(c["value_bool"]) if kind == "boolean" else (c["value_text"] or "Unknown")
                    st = "verified" if c["evidence_category"] == "verified_fact" else c["evidence_category"]
                    cells.append(Cell(disp, st, str(c["id"]), c["value_bool"] if kind == "boolean" else c["value_text"]))
        known = [c for c in cells if c.status not in ("unknown",)]
        differs = len(known) >= 2 and len({(c.raw if c.raw is not None else c.display) for c in known}) > 1
        comp.rows.append(Row(field_key, label, cells, differs))
    unknown_count = sum(1 for r in comp.rows for c in r.cells if c.status == "unknown")
    if unknown_count:
        comp.notes.append(f"{unknown_count} cell(s) are unknown because no verified source states them. Unknown does not mean the feature is absent.")
    return comp


def tradeoffs(comp: Comparison) -> list[str]:
    """Deterministic, evidence-only tradeoff sentences. Never declares a winner."""
    out = []
    rate_row = next((r for r in comp.rows if r.field == "rate.room"), None)
    if rate_row:
        priced = [(comp.entities[i]["name"], c.raw) for i, c in enumerate(rate_row.cells) if isinstance(c.raw, int)]
        if len(priced) >= 2:
            priced.sort(key=lambda t: t[1])
            lo, hi = priced[0], priced[-1]
            if hi[1] != lo[1]:
                out.append(f"On the same {comp.period.replace('_', ' ')}, per-person basis, {lo[0]} is ${(hi[1] - lo[1]) / 100:,.0f} less than {hi[0]} for a {comp.room_type or 'comparable'} room.")
            else:
                out.append(f"{lo[0]} and {hi[0]} have the same {comp.room_type or ''} room rate on this basis.")
    for r in comp.rows:
        if r.field != "rate.room" and r.differs:
            parts = [f"{comp.entities[i]['name']}: {c.display}" for i, c in enumerate(r.cells)]
            out.append(f"{r.label} differs — " + "; ".join(parts) + ".")
    if not out:
        out.append("The verified records do not differ on the compared fields; the decision rests on factors we have not verified.")
    return out
