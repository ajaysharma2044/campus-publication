#!/usr/bin/env python3
"""EduExplained page check. Run on any draft before finishing it.

Usage:
    python3 page_check.py <article.md> [--json]

Exit code 0 = pass, 1 = fail. Prints every problem with the line it is on, so the
writer or editor can fix it directly. Checks only prose: fenced blocks (figures,
tools), tables and frontmatter are skipped, except the repetition check, which also
counts reader blocks and the glance box because that is where most repeats hide.

What it checks, and why (see eduexplained-voice/SKILL.md for the full reasoning):
  repetition   a fact value stated more than twice reads as padding
  opener       the first paragraph is the answer: 60 words or fewer, at most 1 link
  hedges       hedge words hand the decision back to the reader
  narration    "we found", "per X's page read on" is research notes, not an answer
  not-confirmed the "Not confirmed:" label; state a gap once, plainly, with a next step
  time-bound   "this week", "right now" goes stale; anchor advice to a date
  planner-leak SEO and planning talk ("pages that rank", "primary query") on the page
  filler       banned filler words
  format       em dashes, double periods, a money value missing its cents digit
  takeaways    more than 4 key takeaway bullets, or a bullet over 20 words
  readability  Flesch-Kincaid grade of the prose above 10
  unsourced    a paragraph with numbers but no link and no (Source) tag

Fixes applied 2026-11-10 during the idea run: the frontmatter ends at a line that is only ---, so a URL holding --- no
longer ends it early, and a one-line fence (```tool slug```) no longer flips the fence state (it hid everything after it).
"""
import json
import re
import sys
from collections import Counter, defaultdict

MAX_REPEATS = 2            # a fact may appear in its main statement plus one later reference
OPENER_MAX_WORDS = 60
OPENER_MAX_LINKS = 1
HEDGE_PER_1000_MAX = 2.0
READING_GRADE_MAX = 10.0
TITLE_MAX = 60   # Flesch-Kincaid grade of the prose
TAKEAWAYS_MAX = 4          # bullets in the key takeaways (glance) block
TAKEAWAY_MAX_WORDS = 20

HEDGES = r"\b(may|might|typically|generally|usually|often|likely|roughly|reportedly|appears to|seems? to|can vary|it depends|in most cases|tends? to|potentially|possibly)\b"
NARRATION = (r"\b(we found|we could not|we couldn'?t|we did not|we didn'?t|we have not|we will not|we checked|we read|"
             r"we looked|our research|our review|our arithmetic|our sum|by our (?:count|arithmetic|math)|"
             r"the pages we|sources say|it is worth noting|it's worth noting|as of our review|"
             r"read on (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\.? \d+|"
             r"in an? (?:Nov|Oct|Sep)\w* \d+ sample)\b")
TIME_BOUND = r"\b(this week|next week|this month|right now|as of today|if you(?:'re| are) reading this|book (?:it |them |both legs )?now)\b"
PLANNER = r"\b(pages? that rank|ranking pages|search results show|SERP|primary query|our competitors?|AI answers? (?:give|miss|say)|search intent)\b"
FILLER = r"\b(navigat(?:e|ing) the|delve|vibrant|journey|seamless|robust|leverage|unlock|dive into|in today's|game.?changer|look no further)\b"

FACT_RE = re.compile(
    r"\$[\d,]+(?:\.\d+)?"
    r"|\b\d[\d,]*(?:\.\d+)? ?(?:days?|weeks?|months?|years?|hours?|minutes?|miles?|percent|%|credits?|units?)\b"
    r"|\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?|Sept?(?:ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.? \d{1,2}\b")


def split_frontmatter(text):
    """The frontmatter ends at the first line that is only ---, so a URL holding --- cannot end it early."""
    if text.startswith("---"):
        m = re.search(r"^---[ \t]*$", text[3:], flags=re.M)
        if m:
            return text[3:3 + m.start()], text[3 + m.end():], text[: 3 + m.end()].count("\n")
    return "", text, 0


def fence_line(s):
    """0: not a fence line; 1: opens or closes a fenced block; 2: a one-line fence (```tool slug```) that does not."""
    s = s.strip()
    if not s.startswith("```"):
        return 0
    return 2 if len(s) > 6 and s.endswith("```") else 1


def strip_links(s):
    return re.sub(r"\]\([^)]*\)", "]", s)


def prose_lines(body, offset):
    """Yield (line_no, text) for prose only: no fences, tables, headings or images."""
    in_fence = False
    for i, line in enumerate(body.split("\n"), start=offset + 1):
        f = fence_line(line)
        if f:
            if f == 1:
                in_fence = not in_fence
            continue
        if in_fence or line.lstrip().startswith(("|", "#", "![", "<")):
            continue
        yield i, line


def all_text_lines(body, offset):
    """Prose plus reader and glance blocks (for repetition); skip figure/tool fences and tables."""
    fence_kind = None
    for i, line in enumerate(body.split("\n"), start=offset + 1):
        s = line.strip()
        f = fence_line(s)
        if f:
            if f == 1:
                fence_kind = None if fence_kind else (s[3:].split() or ["code"])[0]
            continue
        if fence_kind and fence_kind not in ("reader", "glance"):
            continue
        if s.startswith(("|", "#", "![")):
            continue
        yield i, line


def first_paragraph(body):
    for p in re.split(r"\n\s*\n", body):
        s = p.strip()
        if s and not s.startswith(("#", "|", "-", "*", ">", "<", "!", "`")) and not re.match(r"\d+\.", s):
            return s
    return ""


def syllables(word):
    w = word.lower().strip(".,;:!?'\"()")
    if not w:
        return 0
    if len(w) <= 3:
        return 1
    w = re.sub(r"(?:[^laeiouy]es|ed|[^laeiouy]e)$", "", w)
    w = re.sub(r"^y", "", w)
    return max(1, len(re.findall(r"[aeiouy]{1,2}", w)))


def reading_grade(text):
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", text) if len(s.split()) > 2]
    words = re.findall(r"[A-Za-z][A-Za-z'-]*", text)
    if not sentences or not words:
        return 0.0
    syl = sum(syllables(w) for w in words)
    return 0.39 * len(words) / len(sentences) + 11.8 * syl / len(words) - 15.59


def check(path):
    text = open(path, encoding="utf-8").read()
    fm, body, offset = split_frontmatter(text)
    mode = (re.search(r"^mode:\s*(\w+)", fm, flags=re.M) or [None, "answer"])[1]
    problems = []
    title = (re.search(r'^title:\s*"?(.*?)"?\s*$', fm, flags=re.M) or [None, ""])[1]
    query = (re.search(r'^primary_query:\s*"?(.*?)"?\s*$', fm, flags=re.M) or [None, ""])[1]

    def add(kind, line, msg):
        problems.append({"check": kind, "line": line, "msg": msg})

    # repetition
    seen = defaultdict(list)
    for ln, line in all_text_lines(body, offset):
        for m in FACT_RE.findall(strip_links(line)):
            seen[m.lower().replace(" ", "")].append(ln)
    for fact, lines in sorted(seen.items(), key=lambda kv: -len(kv[1])):
        if len(lines) > MAX_REPEATS:
            add("repetition", lines[0], f"'{fact}' appears {len(lines)} times (lines {', '.join(map(str, lines[:12]))}); state it once, refer back at most once")

    # opener (answer mode only; feature pages open with a scene and state the frame by paragraph 3)
    op = first_paragraph(body) if mode != "feature" else ""
    words = len(strip_links(op).split())
    links = len(re.findall(r"\]\(https?://", op))
    if words > OPENER_MAX_WORDS:
        add("opener", None, f"opening paragraph is {words} words; keep the answer to {OPENER_MAX_WORDS} or fewer and move detail down")
    if links > OPENER_MAX_LINKS:
        add("opener", None, f"opening paragraph has {links} links; keep at most {OPENER_MAX_LINKS}")
    if re.match(r"(No |Nobody|There is no|There are no|.{0,40}(does not|doesn't) publish)", op):
        add("opener", None, "opening leads with what does not exist; lead with what the reader can do")

    # title: under 60 characters, leads with the primary query's words
    if title:
        if len(title) > TITLE_MAX:
            add("title", None, f"title is {len(title)} characters (limit {TITLE_MAX})")
        stop = {"the", "a", "an", "of", "for", "to", "in", "and", "at", "is", "how", "what", "do", "does"}
        qwords = [w for w in re.findall(r"[a-z0-9]+", query.lower()) if w not in stop]
        if qwords:
            hit = sum(1 for w in qwords if w in title.lower())
            if hit / len(qwords) < 0.6:
                add("title", None, f"title holds {hit} of {len(qwords)} primary-query words ('{query}'); lead with what people search")
            first = title.lower().split(":")[0]
            if not any(w in first for w in qwords[:2]):
                add("title", None, "the part before the colon should start with the primary query, not a clever phrase")

    # key takeaways (glance block)
    g = re.search(r"```glance\n(.*?)```", body, flags=re.S)
    if g:
        bullets = [b for b in g.group(1).split("\n") if b.strip().startswith(("-", "*"))]
        if len(bullets) > TAKEAWAYS_MAX:
            add("takeaways", None, f"{len(bullets)} takeaway bullets; keep {TAKEAWAYS_MAX} or fewer")
        for b in bullets:
            n = len(strip_links(b).split()) - 1
            if n > TAKEAWAY_MAX_WORDS:
                add("takeaways", None, f"takeaway bullet is {n} words (limit {TAKEAWAY_MAX_WORDS}): '{b.strip()[:70]}...'")

    # line-level checks
    prose_words = 0
    prose_text = []
    hedge_hits = []
    for ln, line in prose_lines(body, offset):
        plain = strip_links(line)
        prose_words += len(plain.split())
        if plain.strip() and not plain.lstrip().startswith(("-", "*")) and not re.match(r"\s*\d+\.", plain):
            prose_text.append(plain.replace("[", "").replace("]", "").replace("**", ""))
        for m in re.finditer(HEDGES, plain, flags=re.I):
            if m.group(0) == "May" and re.match(r"\s*\d|,? 20\d\d", plain[m.end():]):
                continue  # the month, not the hedge
            hedge_hits.append((ln, m.group(0)))
        for kind, pat in (("narration", NARRATION), ("time-bound", TIME_BOUND), ("planner-leak", PLANNER), ("filler", FILLER)):
            for m in re.finditer(pat, plain, flags=re.I):
                add(kind, ln, f"'{m.group(0)}'")
        if re.search(r"not confirmed:?", plain, flags=re.I):
            add("not-confirmed", ln, "replace the 'Not confirmed' label with one plain sentence: what is unknown and what to do")
        if "\u2014" in line:
            add("format", ln, "em dash")
        if re.search(r"[a-z0-9)]\.\.(?!\.)", line):
            add("format", ln, "double period")
        for m in re.finditer(r"\$\d+\.\d(?!\d)", line):
            add("format", ln, f"'{m.group(0)}' is missing its cents digit")
    rate = 1000 * len(hedge_hits) / max(1, prose_words)
    if rate > HEDGE_PER_1000_MAX:
        sample = ", ".join(f"line {l} '{w}'" for l, w in hedge_hits[:8])
        add("hedges", None, f"{len(hedge_hits)} hedge words ({rate:.1f} per 1,000; limit {HEDGE_PER_1000_MAX}): {sample}")

    # unsourced paragraphs: a paragraph that states numbers or names a rule must carry a link or a (Source) tag
    for para in re.split(r"\n\s*\n", body):
        t = para.strip()
        if not t or t.startswith(("#", "|", "```", "<", "!", "-", "*", "Source", "Prices from", "EduExplained calculation")) or re.match(r"\d+\.", t):
            continue
        if re.search(r"\$\d|\b\d{2,}\b|percent", t) and not re.search(r"\]\(https?://|\]\(/|\([A-Z][^()]{2,80}\)", t):
            ln = offset + body[: body.find(t)].count("\n") + 1
            add("unsourced", ln, f"paragraph states facts with no source: '{t[:70]}...'")

    grade = reading_grade(" ".join(prose_text))
    if grade > READING_GRADE_MAX:
        add("readability", None, f"reading grade {grade:.1f} (limit {READING_GRADE_MAX}); shorter sentences and plainer words")

    return {"file": path, "mode": mode, "reading_grade": round(grade, 1), "pass": not problems, "words": prose_words,
            "counts": dict(Counter(p["check"] for p in problems)), "problems": problems}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    result = check(args[0])
    if "--json" in sys.argv:
        print(json.dumps(result, indent=2))
    else:
        print(f"{'PASS' if result['pass'] else 'FAIL'} {result['file']} ({result['words']} prose words, grade {result['reading_grade']}) {result['counts']}")
        for p in result["problems"]:
            where = f"line {p['line']}: " if p["line"] else ""
            print(f"  [{p['check']}] {where}{p['msg']}")
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
