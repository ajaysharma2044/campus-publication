"""Validate role outputs against the envelope + role schema (SPEC §15).

validate_envelope(doc, role) → list[str] of defects (empty = valid). Also applies rules that JSON
Schema cannot express: next_jobs are proposals only; output must not contain executable commands;
hold decisions need a reason; the output section must match the role's schema.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import best_match
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from ..sanitize import model_output_is_safe

SCHEMA_DIR = Path(__file__).parent / "schemas"
MAX_REPAIR_ATTEMPTS = 1


@lru_cache(maxsize=1)
def _registry() -> Registry:
    reg = Registry()
    for p in SCHEMA_DIR.glob("*.json"):
        doc = json.loads(p.read_text())
        reg = reg.with_resource(doc["$id"], Resource.from_contents(doc, default_specification=DRAFT202012))
    return reg


@lru_cache(maxsize=None)
def _validator(name: str) -> Draft202012Validator:
    doc = json.loads((SCHEMA_DIR / f"{name}.json").read_text())
    return Draft202012Validator(doc, registry=_registry())


def role_schema_name(role: str) -> str:
    return {"opportunity": "opportunity", "researcher": "researcher", "discovery": "discovery", "planner": "planner",
            "writer": "writer", "editor": "editor", "verifier": "verifier", "onboarding": "onboarding", "seo": "seo",
            "tool_engineer": "tool_engineer", "ad_ops": "ad_ops", "analyst": "analyst",
            "skill_scout": "skill_eval", "search_intel": "serp_intel", "search_strategist": "search_strategy"}[role]


def _errors(validator: Draft202012Validator, doc, prefix: str) -> list[str]:
    out = []
    for e in sorted(validator.iter_errors(doc), key=lambda e: list(e.path)):
        # a oneOf/anyOf failure at a high level hides the real defect; report the deepest best-matching sub-error instead
        deep = best_match([e]) if e.context else e
        path = "/".join(str(p) for p in deep.absolute_path) or "<root>"
        msg = deep.message if deep.validator in ("maximum", "minimum", "required", "enum", "type", "maxLength", "minLength", "maxItems", "additionalProperties", "pattern", "minItems") else deep.message[:200]
        out.append(f"schema:{prefix}{path}: {msg[:300]}")
    return out


def validate_envelope(doc: dict, role: str) -> list[str]:
    errs = _errors(_validator("envelope"), doc, "")
    if doc.get("role") not in (None, role):
        errs.append(f"schema:role mismatch: envelope says {doc.get('role')}, expected {role}")
    if isinstance(doc.get("output"), dict):
        errs += _errors(_validator(role_schema_name(role)), doc["output"], "output/")
    # Rules beyond schema
    if doc.get("decision") == "hold" and not doc.get("hold"):
        errs.append("schema:hold decision without machine-readable hold reason")
    for s in _strings(doc.get("output", {})):
        errs += model_output_is_safe(s)
    for nj in doc.get("next_jobs", []) or []:
        payload = nj.get("payload") or {}
        for forbidden in ("budget", "cap", "quota", "permission", "grant", "api_key", "shell", "command"):
            if forbidden in json.dumps(payload).lower():
                errs.append(f"schema:next_jobs payload attempts control-plane change ({forbidden})")
                break
    return errs


def _strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _strings(v)


def parse_model_json(text: str) -> tuple[dict | None, list[str]]:
    """Extract the first JSON object from model text. Tolerates ```json fences. Never evals."""
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else t
        t = t.rsplit("```", 1)[0]
    start, end = t.find("{"), t.rfind("}")
    if start < 0 or end <= start:
        return None, ["schema:no JSON object in output"]
    try:
        return json.loads(t[start:end + 1]), []
    except json.JSONDecodeError as e:
        return None, [f"schema:invalid JSON: {e.msg} at {e.pos}"]


def validator_for(role: str):
    """Return a validate(text)->defects callable for ModelRouter.call()."""
    def _v(text: str) -> list[str]:
        doc, errs = parse_model_json(text)
        if errs:
            return errs
        return validate_envelope(doc, role)
    return _v
