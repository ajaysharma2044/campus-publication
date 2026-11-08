"""PreToolUse guard (Footnote Daily v2, owner spec 2026-11-07): the only rule left is the .env block.
Secrets live in worker/.env; Claude never reads, prints or copies a .env file. Sourcing one from a script
(`set -a; . worker/.env; set +a`) stays allowed, since that is how scripts get their credentials."""
import json, re, sys

try:
    d = json.load(sys.stdin)
except Exception as e:  # noqa: BLE001
    print(f"guard: cannot parse hook input ({e}); blocked", file=sys.stderr); sys.exit(2)
tool = d.get("tool_name", ""); ti = d.get("tool_input", {}) or {}


def block(msg):
    print(f"guard: BLOCKED — {msg}", file=sys.stderr); sys.exit(2)


ENV_PATH = re.compile(r"(^|[/\s'\"])\.env(\.[A-Za-z0-9_-]+)?($|[\s'\"])")
READERS = r"\b(cat|less|more|head|tail|grep|egrep|fgrep|rg|ag|awk|sed|cut|sort|uniq|strings|xxd|od|hexdump|base64|cp|scp|rsync|tee|install|zip|tar|python[0-9.]*\s+-c|node\s+-e|open|pbcopy|curl|wget)\b"

if tool in ("Read", "Edit", "Write", "MultiEdit", "NotebookEdit"):
    path = str(ti.get("file_path") or ti.get("notebook_path") or "")
    if ENV_PATH.search(path):
        block("a .env file holds secrets Claude never reads or writes")
elif tool == "Bash":
    cmd = ti.get("command", "") or ""
    for segment in re.split(r"[|;&]+", cmd):
        if ENV_PATH.search(segment) and re.search(READERS, segment):
            block("shell command that reads or copies a .env file")
    if re.search(r"(^|[|;&]\s*)(printenv|env|export -p|set)\s*($|[|;&>])", cmd):
        block("dumping the environment would print the secrets loaded from .env")
sys.exit(0)
