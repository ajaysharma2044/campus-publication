#!/usr/bin/env python3
"""Validate an agent's handoff file against its schema. Code runs this between every
pair of agents; agents also run it on their own output before finishing.

Usage:
    python3 scripts/validate_handoff.py schemas/<name>.schema.json <file.json>

Uses the `jsonschema` package when installed; otherwise a built-in checker covering
the subset our schemas use (type, required, properties, items, minItems, enum,
minLength, maxLength, pattern). Exit 0 = valid, 1 = invalid.
"""
import json
import re
import sys

TYPES = {"object": dict, "array": list, "string": str, "integer": int, "number": (int, float), "boolean": bool, "null": type(None)}


def check(node, schema, path, errors):
    t = schema.get("type")
    if t:
        ts = t if isinstance(t, list) else [t]
        ok = any(isinstance(node, TYPES[x]) and not (x in ("integer", "number") and isinstance(node, bool)) for x in ts)
        if not ok:
            errors.append(f"{path}: expected {t}, got {type(node).__name__}")
            return
    if "enum" in schema and node not in schema["enum"]:
        errors.append(f"{path}: {node!r} not in {schema['enum']}")
    if isinstance(node, str):
        if len(node) < schema.get("minLength", 0):
            errors.append(f"{path}: shorter than {schema['minLength']} characters")
        if "maxLength" in schema and len(node) > schema["maxLength"]:
            errors.append(f"{path}: {len(node)} characters, longer than {schema['maxLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], node):
            errors.append(f"{path}: does not match {schema['pattern']}")
    if isinstance(node, dict):
        for key in schema.get("required", []):
            if key not in node:
                errors.append(f"{path}: missing required '{key}'")
        for key, sub in schema.get("properties", {}).items():
            if key in node:
                check(node[key], sub, f"{path}.{key}", errors)
    if isinstance(node, list):
        if len(node) < schema.get("minItems", 0):
            errors.append(f"{path}: needs at least {schema['minItems']} items, has {len(node)}")
        if "items" in schema:
            for i, item in enumerate(node):
                check(item, schema["items"], f"{path}[{i}]", errors)


def main(schema_path, data_path):
    schema = json.load(open(schema_path, encoding="utf-8"))
    data = json.load(open(data_path, encoding="utf-8"))
    try:
        import jsonschema
        errors = [f"{'/'.join(map(str, e.path)) or '$'}: {e.message}" for e in jsonschema.Draft202012Validator(schema).iter_errors(data)]
    except ImportError:
        errors = []
        check(data, schema, "$", errors)
    print(f"{'VALID' if not errors else 'INVALID'} {data_path} against {schema_path}" + (f" ({len(errors)} errors)" if errors else ""))
    for e in errors[:40]:
        print("  ", e)
    return 0 if not errors else 1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2]))
