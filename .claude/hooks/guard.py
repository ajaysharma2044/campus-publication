import json, os, re, sys
root = sys.argv[1]
try:
    d = json.load(sys.stdin)
except Exception as e:  # noqa: BLE001
    print(f"guard: cannot parse hook input ({e}); blocked", file=sys.stderr); sys.exit(2)
tool = d.get("tool_name", ""); ti = d.get("tool_input", {}) or {}

def rel(p):
    if not p: return ""
    p = os.path.abspath(os.path.join(root, p)) if not os.path.isabs(p) else os.path.abspath(p)
    return os.path.relpath(p, root)

def block(msg):
    print(f"guard: BLOCKED — {msg} (specs/continuous-local-run.md §7). Propose changes in STATE.md under 'Proposed spec changes'.", file=sys.stderr); sys.exit(2)

GATE_RE = re.compile(r"^\s*(MIN_TOTAL|MIN_EACH|RUBRIC_KEYS|HARD_KINDS)\s*=", re.M)
RAMP_RE = re.compile(r"(CAMPUS_LIVE_RAMP|live_ramp\s*:)")
RAMP_DEFAULT = '"5x14,15"'

def adopted_skills():
    f = os.path.join(root, "docs/ops/skill-evaluations.md")
    try: text = open(f, encoding="utf-8").read()
    except FileNotFoundError: return set()
    out = set()
    for line in text.splitlines():
        if "|" not in line: continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and any(c.lower() in ("adopted", "baseline (in-repo)") for c in cells):
            name = cells[0].strip("`")
            if any(re.fullmatch(r"[0-9a-f]{40}", c) or c == "in-repo" for c in cells):
                out.add(name)
    return out

def check_path(path, old, new, content, is_write):
    r = rel(path)
    if r == "SPEC.md" or r.startswith("specs/") or r.startswith("specs" + os.sep):
        block(f"edit to {r}: the spec is owner-only")
    if r == ".claude/settings.json":
        block("edit to .claude/settings.json: guard rules are owner-only")
    if r == "worker/campus_worker/editorial/gates.py":
        if is_write: block("Write to gates.py: use Edit so gate constants can be checked")
        if GATE_RE.search(old or "") or GATE_RE.search(new or ""):
            block("edit touches gate threshold constants (MIN_TOTAL/MIN_EACH/RUBRIC_KEYS/HARD_KINDS)")
    if r == "worker/campus_worker/config.py":
        txt = (new if not is_write else content) or ""
        for line in txt.splitlines():
            if RAMP_RE.search(line) and RAMP_DEFAULT not in line and "from_env" not in line and "#" not in line.split("=")[0]:
                block(f"edit changes the live-ramp default (must stay {RAMP_DEFAULT}): {line.strip()[:80]}")
        if (old or "") and RAMP_RE.search(old) and RAMP_DEFAULT in old and RAMP_DEFAULT not in (new or ""):
            block("edit removes the live-ramp default")
    if r.startswith(".claude/skills/"):
        name = r.split("/")[2] if len(r.split("/")) > 2 else ""
        if name and name not in adopted_skills():
            block(f"write into .claude/skills/{name}: not listed as adopted (with SHA) in docs/ops/skill-evaluations.md")

if tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
    path = ti.get("file_path") or ti.get("notebook_path") or ""
    if tool == "MultiEdit":
        for e in ti.get("edits", []) or []:
            check_path(path, e.get("old_string"), e.get("new_string"), None, False)
    else:
        check_path(path, ti.get("old_string"), ti.get("new_string"), ti.get("content"), tool in ("Write", "NotebookEdit"))
elif tool == "Bash":
    cmd = ti.get("command", "") or ""
    if re.search(r"git\s+push\b.*(\s--force\b|\s-f\b|--force-with-lease)", cmd):
        block("force push")
    writeish = re.search(r"(>{1,2}|\bsed\s+-i|\bperl\s+-p?i|\btee\b|\bcp\b|\bmv\b|\brm\b|\bln\b|\btruncate\b|\bdd\b|\bpython[0-9.]*\s+-\s*<<|\bcat\s*<<|\bgit\s+checkout\s+--|\bgit\s+restore\b)", cmd)
    if writeish:
        for pat, what in ((r"\bSPEC\.md\b", "SPEC.md"), (r"\bspecs/", "specs/"), (r"\.claude/settings\.json", ".claude/settings.json"),
                          (r"editorial/gates\.py", "gates.py"), (r"campus_worker/config\.py", "config.py")):
            if re.search(pat, cmd):
                block(f"shell write touching {what}")
        m = re.search(r"\.claude/skills/([A-Za-z0-9_.-]+)", cmd)
        if m and m.group(1) not in adopted_skills():
            block(f"shell write into .claude/skills/{m.group(1)}: not listed as adopted in docs/ops/skill-evaluations.md")
sys.exit(0)
