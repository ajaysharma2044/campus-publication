#!/usr/bin/env python
"""v3 topic intelligence brief (docs/v3/spec.md, section 2; Speed mode rule 1: facts are verified once, in the brief).

    scripts/v3/brief.sh <topic> [--model opus] [--max-turns 200] [--check-model sonnet] [--skip-check] [--resume]
                                [--check-max-turns 80] [--check-workers 5] [--timeout 10800] [--check-timeout 3600] [--intel-dir DIR]

1. Synthesis: one session (opus) reads every file under intel/<topic>/raw/ and writes intel/<topic>/brief.md with the 11 sections
   (prompts/brief.md): the skeleton first, then section by section with Edit, 15,000 to 40,000 words, every fact row with Source URL,
   Applies to and Checked. An existing brief is moved to build/runs/v2/brief/ first, unless --resume (keep it; only expand and check).
2. Expand: when the brief is under 15,000 words, one more session with the same prompt in MODE expand adds depth from the lanes.
3. Check: one sonnet session per lane (official, market, voice, competition, analysis; five in parallel) opens the sources behind
   that lane's facts, fixes the brief in place and writes its findings to intel/<topic>/checks/<lane>.md; the driver appends those to
   intel/<topic>/brief-check.md and removes the parts. --skip-check skips this step.
Prints the word count, the presence and size of each section, the fact-row count and the check totals; exit 1 when the brief is
missing a section or is under 15,000 words. Log: build/runs/v2/brief-<ts>.log; stop with .run/STOP (scripts/v2/stop.sh); a usage
limit pauses and resumes on its own (scripts/v2/lib/sessions.py).

These sessions are the one place a pipeline session gets Edit (scoped to the intel folder): sessions.py disallows Edit for every v2
step, and allow_edit() lifts that for this process only. scripts/v3/plan.py and readers.sh import the helpers below.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "v2"))
from lib import sessions  # noqa: E402

PROMPTS = REPO / "scripts" / "v3" / "prompts"
TOPICS_FILE = REPO / "scripts" / "v3" / "topics.yml"
LANES = ("official", "market", "voice", "competition", "analysis")
LANE_NOTES = {  # what each lane holds, and the brief sections drawn mostly from it (the check prompt gets both)
    "official": ("rules, prices, fees, deadlines, forms, offices, phone numbers and policies from official pages", "2, 4 and 6"),
    "market": ("listings, rent ranges, landlords and companies, lease timing, utilities and insurance costs, counted things with sample sizes", "3 and 5"),
    "voice": ("recurring student experiences, tips, complaints and myths, attributed and linked", "6 and 7"),
    "competition": ("what ranks and what AI answers say for the topic's questions, and what they get wrong or leave out", "1 and 9"),
    "analysis": ("our own computed numbers and patterns, with method, sample size and date", "3, 8 and 10"),
}
SECTIONS = [(1, "The topic in one page"), (2, "Fact base"), (3, "Numbers"), (4, "Timeline"), (5, "Places and players"),
            (6, "How it actually works"), (7, "Student voice"), (8, "Contradictions and unknowns"),
            (9, "What the competition and AI answers miss"), (10, "Original analysis"), (11, "Change log")]
MIN_WORDS, MAX_WORDS = 15_000, 40_000
URL_RE = re.compile(r"https?://\S+")
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['’.,:/-][A-Za-z0-9]+)*")
HEADING_RE = re.compile(r"^## (\d+)\. (.+?)\s*$", re.M)
ALIGN_RE = re.compile(r"^\s*\|[\s:|-]+\|?\s*$")
RESULT_RE = re.compile(r"\|\s*(ok|fixed|unverifiable)\s*\|", re.I)


# ------------------------------------------------------------------------------------------ shared helpers (plan.py, readers.sh)
def topics() -> dict[str, dict]:
    return {t["slug"]: t for t in yaml.safe_load(TOPICS_FILE.read_text(encoding="utf-8"))}


def topic_or_exit(slug: str) -> dict:
    t = topics().get(slug)
    if not t:
        sys.exit(f"unknown topic {slug!r}; see scripts/v3/topics.yml")
    return t


def intel_root(arg: str | None) -> Path:
    """intel/ in the repo, or the --intel-dir override (tests point it at a temp folder)."""
    return Path(arg).resolve() if arg else REPO / "intel"


def rel(path: Path | str) -> str:
    """The path as a session sees it: relative to the repo when inside it (sessions run with cwd = repo), else absolute."""
    p = Path(path).resolve()
    try:
        return str(p.relative_to(REPO))
    except ValueError:
        return str(p)


def tool_rule(tool: str, folder: Path) -> str:
    """A claude permission rule for one tool under one folder: Write(intel/**) inside the repo, Write(//abs/path/**) outside it."""
    r = rel(folder)
    return f"{tool}({r}/**)" if not r.startswith("/") else f"{tool}(/{r}/**)"


def words(text: str) -> int:
    """Words of prose and table cells; URLs and table pipes do not count."""
    return len(WORD_RE.findall(URL_RE.sub(" ", text)))


def fact_rows(text: str) -> int:
    """Table rows that carry a source URL: the brief's unit of fact."""
    return sum(1 for line in text.splitlines() if line.lstrip().startswith("|") and "http" in line and not ALIGN_RE.match(line))


def sections(text: str) -> list[dict]:
    """For each of the 11 expected sections: n, title, present, words (from its heading to the next numbered level-2 heading)."""
    heads = list(HEADING_RE.finditer(text))
    out = []
    for n, title in SECTIONS:
        hit = next((i for i, m in enumerate(heads) if int(m.group(1)) == n and m.group(2).strip().lower().startswith(title.lower())), None)
        if hit is None:
            out.append({"n": n, "title": title, "present": False, "words": 0})
            continue
        end = heads[hit + 1].start() if hit + 1 < len(heads) else len(text)
        out.append({"n": n, "title": title, "present": True, "words": words(text[heads[hit].end():end])})
    return out


def missing_sections(brief: Path) -> list[str]:
    if not brief.exists():
        return [f"missing {rel(brief)}"]
    return [f"section {s['n']} ({s['title']}) missing" for s in sections(brief.read_text(encoding="utf-8")) if not s["present"]]


def lane_files(raw: Path, lane: str) -> list[Path]:
    """A lane's notes: official.md plus any official-02-....md a long session split off."""
    return sorted(p for p in raw.glob(f"{lane}*.md") if p.is_file())


def raw_files(raw: Path) -> list[Path]:
    return sorted(p for p in raw.glob("*.md") if p.is_file()) if raw.is_dir() else []


def file_list(paths: list[Path]) -> str:
    return "\n".join(f"- {rel(p)} ({words(p.read_text(encoding='utf-8')):,} words)" for p in paths) or "- (none)"


def allow_edit() -> None:
    """Lift Edit from sessions.DISALLOWED_TOOLS for this process: the brief is filled and corrected in place. Bash, MultiEdit,
    NotebookEdit, Agent and Task stay disallowed; the allowed-tools list scopes Edit to the intel folder."""
    sessions.DISALLOWED_TOOLS = ",".join(t for t in sessions.DISALLOWED_TOOLS.split(",") if t != "Edit")


# ------------------------------------------------------------------------------------------ reports
def status_text(brief: Path) -> str:
    if not brief.exists():
        return "The brief does not exist yet."
    text = brief.read_text(encoding="utf-8")
    per = ", ".join(f"{s['n']}: {s['words']:,}" if s["present"] else f"{s['n']}: missing" for s in sections(text))
    return f"The brief exists with {words(text):,} words and {fact_rows(text)} fact rows with a source URL. Words per section: {per}."


def report(brief: Path, log=print) -> bool:
    text = brief.read_text(encoding="utf-8") if brief.exists() else ""
    n, secs = words(text), sections(text)
    log(f"brief {rel(brief)}: {n:,} words (target {MIN_WORDS:,} to {MAX_WORDS:,}); {fact_rows(text)} fact rows with a source URL")
    for s in secs:
        log(f"  {s['n']:>2}. {s['title']:<42} {'present' if s['present'] else 'MISSING'} {s['words']:>7,} words")
    if n > MAX_WORDS:
        log(f"  note: over {MAX_WORDS:,} words; the next refresh should merge rows, not add")
    return bool(text) and all(s["present"] for s in secs) and n >= MIN_WORDS


def merge_checks(checks: Path, check_file: Path, topic: str, today: str, log=print) -> dict:
    """Append each lane's findings (intel/<topic>/checks/<lane>.md) to intel/<topic>/brief-check.md and remove the parts."""
    totals: Counter = Counter()
    if not check_file.exists():
        check_file.write_text(f"# Brief fact checks: {topic}\n\nOne sonnet pass per research lane over intel/{topic}/brief.md (docs/v3/spec.md, Speed mode 1). "
                              "Appended by scripts/v3/brief.sh; the newest run is at the bottom. Result per fact: ok, fixed (the brief was corrected in place) "
                              "or unverifiable (the source could not be opened or does not hold the fact).\n", encoding="utf-8")
    for lane in LANES:
        part = checks / f"{lane}.md"
        if not part.exists():
            continue
        text = part.read_text(encoding="utf-8").strip()
        if not text.startswith("#"):
            text = f"## Lane {lane}, checked {today}\n\n{text}"
        with check_file.open("a", encoding="utf-8") as fh:
            fh.write("\n" + text + "\n")
        c = Counter(m.group(1).lower() for m in RESULT_RE.finditer(text))
        totals.update(c)
        log(f"  {lane}: {c.get('ok', 0)} ok, {c.get('fixed', 0)} fixed, {c.get('unverifiable', 0)} unverifiable; appended to {rel(check_file)}")
        part.unlink()
    if checks.is_dir() and not any(checks.iterdir()):
        checks.rmdir()
    return dict(totals)


# ------------------------------------------------------------------------------------------ the step
def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="brief.sh", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("topic")
    ap.add_argument("--model", default="opus", help="synthesis and expand sessions (default opus)")
    ap.add_argument("--max-turns", type=int, default=200)
    ap.add_argument("--check-model", default="sonnet")
    ap.add_argument("--check-max-turns", type=int, default=80)
    ap.add_argument("--check-workers", type=int, default=5)
    ap.add_argument("--skip-check", action="store_true", help="no fact-check sessions")
    ap.add_argument("--resume", action="store_true", help="keep an existing brief: only expand it when short and check it")
    ap.add_argument("--timeout", type=int, default=10800, help="seconds per synthesis or expand session")
    ap.add_argument("--check-timeout", type=int, default=3600)
    ap.add_argument("--intel-dir", default=None, help="intel folder (default intel/)")
    a = ap.parse_args(argv)
    t = topic_or_exit(a.topic)
    tdir = intel_root(a.intel_dir) / a.topic
    raw = tdir / "raw"
    files = raw_files(raw)
    lanes = {lane: lane_files(raw, lane) for lane in LANES if lane_files(raw, lane)}
    if not lanes:
        print(f"no lane notes under {rel(raw)}/ (official*.md, market*.md, voice*.md, competition*.md, analysis*.md); run scripts/v3/research.sh {a.topic} first", file=sys.stderr)
        return 2
    brief, check_file, checks = tdir / "brief.md", tdir / "brief-check.md", tdir / "checks"
    demand = raw / "demand-questions.md"
    log, log_path = sessions.open_log("brief")
    sessions.clear_stop(log)
    allow_edit()
    today = date.today().isoformat()
    log(f"brief for {t['title']} ({a.topic}): {len(files)} raw files in {len(lanes)} lanes ({', '.join(lanes)}); synthesis {a.model}, {a.max_turns} turns; "
        f"checks {a.check_model}, {a.check_max_turns} turns, {a.check_workers} workers{' (skipped)' if a.skip_check else ''}{'; resume' if a.resume else ''}")
    template = (PROMPTS / "brief.md").read_text(encoding="utf-8")
    tools = ",".join(["Read", "Grep", "Glob", tool_rule("Write", tdir), tool_rule("Edit", tdir)])

    def run_brief(mode: str, label: str) -> dict:
        prompt = sessions.fill(template, today=today, topic_title=t["title"], topic_scope=t["scope"], topic_slug=a.topic, topic_dir=t["dir"],
                               brief_path=rel(brief), raw_files=file_list(files), mode=mode, status=status_text(brief), max_turns=a.max_turns,
                               min_words=f"{MIN_WORDS:,}", max_words=f"{MAX_WORDS:,}",
                               demand_path=rel(demand) if demand.exists() else "(none exported yet; research.sh writes raw/demand-questions.md)")
        sessions.save_prompt(label, a.topic, prompt)
        job = {"id": f"{a.topic}:{mode}", "prompt": prompt, "expect": [str(brief)], "check": lambda: missing_sections(brief)}
        return sessions.run_jobs([job], workers=1, label=label, model=a.model, max_turns=a.max_turns, allowed_tools=tools, timeout_s=a.timeout, log=log)

    # 1. synthesis
    if brief.exists() and a.resume:
        log(f"resume: {rel(brief)} exists ({words(brief.read_text(encoding='utf-8')):,} words); synthesis skipped")
    else:
        if brief.exists():
            keep = sessions.RUNS / "brief" / f"{a.topic}-brief-{datetime.now().strftime('%Y%m%dT%H%M%S')}.md"
            keep.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(brief), str(keep))
            log(f"existing brief moved to {rel(keep)} (--resume keeps it in place instead)")
        st = run_brief("write", "brief")
        if not brief.exists():
            log("no brief was written; stopping")
            return 1
        if st["failed"]:
            log(f"synthesis ended with problems ({'; '.join(missing_sections(brief)) or 'see the session file'}); continuing with what was written")
    if sessions.stopped():
        log("STOP file found; stopping after synthesis")
        report(brief, log)
        return 1
    # 2. expand when short
    n = words(brief.read_text(encoding="utf-8"))
    if n < MIN_WORDS:
        log(f"brief has {n:,} words, under {MIN_WORDS:,}: one expand session")
        run_brief("expand", "brief-expand")
        log(f"after expand: {words(brief.read_text(encoding='utf-8')):,} words")
    # 3. one fact-check session per lane
    totals: dict = {}
    if a.skip_check:
        log("fact check skipped (--skip-check)")
    elif sessions.stopped():
        log("STOP file found; fact check not started")
    else:
        check_template = (PROMPTS / "brief-check.md").read_text(encoding="utf-8")
        checks.mkdir(parents=True, exist_ok=True)
        check_tools = ",".join(["Read", "Grep", "Glob", "WebFetch", "WebSearch", tool_rule("Write", tdir), tool_rule("Edit", tdir)])
        jobs = []
        for lane, lfiles in lanes.items():
            out = checks / f"{lane}.md"
            if out.exists():
                out.unlink()
            desc, secs = LANE_NOTES[lane]
            prompt = sessions.fill(check_template, today=today, topic_title=t["title"], topic_slug=a.topic, brief_path=rel(brief), lane=lane, lane_desc=desc,
                                   lane_sections=secs, lane_files=file_list(lfiles), out_path=rel(out), max_turns=a.check_max_turns)
            sessions.save_prompt("brief-check", f"{a.topic}-{lane}", prompt)
            jobs.append({"id": f"{a.topic}:{lane}", "prompt": prompt, "expect": [str(out)]})
        log(f"{len(jobs)} fact-check session(s) with {a.check_model}, {a.check_workers} workers")
        sessions.run_jobs(jobs, workers=a.check_workers, label="brief-check", model=a.check_model, max_turns=a.check_max_turns,
                          allowed_tools=check_tools, timeout_s=a.check_timeout, log=log)
        totals = merge_checks(checks, check_file, a.topic, today, log)
    # 4. report
    ok = report(brief, log)
    if totals:
        log(f"checks this run: {totals.get('ok', 0)} ok, {totals.get('fixed', 0)} fixed, {totals.get('unverifiable', 0)} unverifiable -> {rel(check_file)}")
    log(f"brief {'complete' if ok else 'NOT complete yet'}: {rel(brief)}; log {rel(log_path)}; next: scripts/v3/readers.sh {a.topic}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
