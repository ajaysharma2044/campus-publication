"""Inline SVG figures built deterministically from a page's verified fact table.

Owner ask (2026-11-06): "pictures and stuff in the writing", at higher quality, under the hard rules: no stock
photography, no model-generated imagery, no fabricated facts. So every figure here is a pure function of the
fact-table rows (plus the page's own step list): labels are the rows' labels, every number is printed exactly as
the row prints it, and a figure exists only when the rows support it. No network, no PIL. Colors are the
campus.css tokens (the same hex as fallbacks, so a figure viewed without the stylesheet keeps the palette) and the
SVG scales with the content width through its viewBox; there are no fixed pixel widths.
"""
from __future__ import annotations

import html
import re
import textwrap
from datetime import date
from decimal import Decimal, InvalidOperation

W = 360            # viewBox width: the article column on a 360px phone; wider columns scale the figure up (CSS caps it at 36rem)
PAD = 12
LINE = 16          # line box for 13px text
WRAP = 46          # characters per line at 13px across the viewBox (~48 asked; 46 leaves the axis margin)
MAX_BARS = 8
MAX_DATES = 8
MAX_STEPS = 6
FULL_VALUE_CHARS = 22  # a bar prints its row's whole value when every value in the chart is this short, else the amount alone

# campus.css tokens with the stylesheet's own hex values as fallbacks
NAVY = "var(--navy, #1F5A4A)"
INK = "var(--ink, #1B1B1B)"
INK_2 = "var(--ink-2, #4F4F4F)"
INK_3 = "var(--ink-3, #6B6B6B)"
RULE_STRONG = "var(--rule-strong, #C9C5BB)"
SURFACE = "var(--surface, #FFFFFF)"
FONT = "var(--font-sans, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif)"

MONEY = re.compile(r"\$\s?(\d{1,3}(?:,\d{3})+|\d+)(?:\.(\d{2}))?")              # the shape editorial.checks.MONEY_PATTERN matches
RANGE = re.compile(r"\$\s?[\d,]+(?:\.\d{2})?\s*(?:–|—|-|to)\s*\$?\s?\d")        # "$6,322–$6,872": one bar cannot show a range honestly
SEMESTER = re.compile(r"\b(?:per|each|a|every)[\s-]+semester\b|/\s*semester\b|\bper[\s-]+term\b", re.I)
ACADEMIC_YEAR = re.compile(r"\bacademic[\s-]+year\b|\b(?:per|each|a|every)[\s-]+year\b|/\s*(?:yr|year)\b|\bannual(?:ly)?\b|\byearly\b", re.I)
PERIOD_TITLE = {"semester": "Per-semester amounts at a glance", "academic_year": "Academic-year amounts at a glance", "other": "Amounts at a glance"}

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
MONTH_INDEX = {m[:3].lower(): i + 1 for i, m in enumerate(MONTHS)}
DATE_WORDS = re.compile(r"\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(20\d{2})\b")
DATE_ISO = re.compile(r"\b(20\d{2})-(\d{2})-(\d{2})\b")
# a dated row joins the timeline when its label or value reads like a deadline or a scheduled date; a historical date
# ("halls opened August 15, 2022") stays out, so "passed" is never pinned on something that was never due
DEADLINE_WORDS = re.compile(r"\b(?:deadlines?|due|apply|applies|applications?|sign-?ups?|register|registration|cancels?|cancellations?|move-?in|move-?out|opens?|closes?|closing|"
                            r"begins?|starts?|ends?|last day|first day|notifications?|notified|decisions?|released?|payments?|billing|bills?|refunds?|confirm|confirmations?|"
                            r"priority|window|lottery|selection|renewals?|contracts?|submit|submission|requests?|withdraw|withdrawal|orientation|check-?in|check-?out|passed|"
                            r"term|semester|fall|spring|summer|winter)\b", re.I)


# ------------------------------------------------------------------------------------------------ small SVG helpers
def _t(s) -> str:
    return html.escape(str(s), quote=True)


def _n(v) -> str:
    s = f"{float(v):.1f}"
    return s[:-2] if s.endswith(".0") else s


def _wrap(text, width: int, max_lines: int) -> list[str]:
    lines = textwrap.wrap(" ".join(str(text).split()), width=width, break_long_words=True) or [""]
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][: max(1, width - 1)].rstrip() + "…"
    return lines


def _size(size: int | None) -> str:
    return f' font-size="{size}"' if size else ""   # no size: inherit the root's 13, which campus.css raises to 14 on phones


def _text(x, y, s, *, size: int | None = None, fill: str = INK, weight: str = "400", anchor: str = "start") -> str:
    return f'<text x="{_n(x)}" y="{_n(y)}"{_size(size)} font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{_t(s)}</text>'


def _lines(x, y, lines: list[str], *, size: int | None = None, fill: str = INK, weight: str = "400") -> str:
    spans = "".join(f'<tspan x="{_n(x)}" dy="{0 if i == 0 else LINE}">{_t(line)}</tspan>' for i, line in enumerate(lines))
    return f'<text x="{_n(x)}" y="{_n(y)}"{_size(size)} font-weight="{weight}" fill="{fill}">{spans}</text>'


def _badge(x, y, n: int, *, passed: bool = False, r: int = 9) -> str:
    fill, stroke, color = (SURFACE, INK_3, INK_3) if passed else (NAVY, NAVY, "#fff")
    return (f'<g class="badge{" badge--passed" if passed else ""}"><circle cx="{_n(x)}" cy="{_n(y)}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
            + _text(x, y + 4, str(n), size=11, fill=color, weight="700", anchor="middle") + "</g>")


def _svg(kind: str, title: str, desc: str, height: float, body: str) -> str:
    h = int(round(height))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="100%" height="{h}" role="img" '
            f'aria-labelledby="fig-{kind}-title" aria-describedby="fig-{kind}-desc" font-size="13" style="font-family:{FONT};max-width:100%">'
            f'<title id="fig-{kind}-title">{_t(title)}</title><desc id="fig-{kind}-desc">{_t(desc)}</desc>{body}</svg>')


def date_text(d: date) -> str:
    """The style guide's date form: 'November 6, 2026'."""
    return f"{MONTHS[d.month - 1]} {d.day}, {d.year}"


# ------------------------------------------------------------------------------------------------ money rows → bar chart
def _period(label: str, value: str) -> str:
    amounts = list(MONEY.finditer(value))
    head = value[: amounts[1].start()] if len(amounts) > 1 else value   # "$6,872 per semester, per person ($13,744/yr)": classify by the first amount's words
    text = f"{label} {head}"
    if SEMESTER.search(text):
        return "semester"
    if ACADEMIC_YEAR.search(text):
        return "academic_year"
    return "other"


def money_rows(rows: list[dict] | None) -> list[dict]:
    """Rows whose value carries a dollar amount: label, verbatim value, the first amount as printed, and its billing period."""
    out = []
    for r in rows or []:
        if not isinstance(r, dict):
            continue
        label, value = " ".join(str(r.get("label") or "").split()), " ".join(str(r.get("value") or "").split())
        m = MONEY.search(value)
        if not label or not m or RANGE.search(value):
            continue
        try:
            amount = Decimal(m.group(0).replace("$", "").replace(",", "").strip())
        except InvalidOperation:
            continue
        out.append({"label": label, "value": value, "amount_text": m.group(0).strip(), "amount": amount, "period": _period(label, value)})
    return out


def cost_chart(rows: list[dict] | None, period: str | None = None) -> dict | None:
    """Horizontal bars for the money rows of one billing period: per-semester rows when at least two exist, else
    academic-year rows, else the rows with no stated period. Bars start at zero; the number by each bar is the
    row's own text. None when fewer than two rows share a period."""
    money = money_rows(rows)
    groups = {p: [m for m in money if m["period"] == p] for p in ("semester", "academic_year", "other")}
    if period is None:
        period = next((p for p in ("semester", "academic_year", "other") if len(groups[p]) >= 2), None)
    if period is None or len(groups.get(period, [])) < 2:
        return None
    items, truncated = groups[period][:MAX_BARS], len(groups[period]) > MAX_BARS
    full = all(len(m["value"]) <= FULL_VALUE_CHARS for m in items)
    printed = [m["value"] if full else m["amount_text"] for m in items]
    reserve = max(len(p) for p in printed) * 6.6 + 8                      # room for the printed value after the longest bar
    bar_max = max(120.0, W - 2 * PAD - reserve)
    top = max(float(m["amount"]) for m in items)
    x0, y, parts = PAD, PAD, []
    for m, p in zip(items, printed):
        lines = _wrap(m["label"], WRAP, 3)
        parts.append(_lines(x0, y + 12, lines))
        y_bar = y + len(lines) * LINE + 3
        w = bar_max * float(m["amount"]) / top if top else 0.0
        parts.append(f'<rect x="{x0}" y="{_n(y_bar)}" width="{_n(w)}" height="14" rx="2" fill="{NAVY}"><title>{_t(m["label"])}: {_t(m["value"])}</title></rect>')
        parts.append(_text(x0 + w + 6, y_bar + 11, p, weight="700"))
        y = y_bar + 14 + 14
    height = y - 14 + PAD
    axis = f'<line x1="{x0}" y1="{PAD}" x2="{x0}" y2="{_n(height - PAD)}" stroke="{RULE_STRONG}" stroke-width="1"/>'
    caption = "Each bar is a row of the fact table above, drawn from zero; the amounts are printed exactly as the table gives them."
    if not full:
        caption += " The number by each bar is the first dollar amount in that row; the table gives the basis."
    if truncated:
        caption += f" The first {MAX_BARS} such rows are shown."
    title = PERIOD_TITLE[period]
    desc = "; ".join(f"{m['label']}: {m['value']}" for m in items)
    return {"kind": "cost", "title": title, "svg": _svg("cost", title, desc, height, axis + "".join(parts)), "caption": caption}


# ------------------------------------------------------------------------------------------------ dated rows → timeline
def _safe_date(y: int, m: int | None, d: int) -> date | None:
    try:
        return date(y, m, d) if m else None
    except ValueError:
        return None


def first_date(text: str) -> date | None:
    """The first full date in a value: 'June 15, 2026', 'Sept. 1, 2026' or '2026-06-15'. A month-and-year alone is not a date."""
    best: tuple[int, date] | None = None
    for m in DATE_WORDS.finditer(text):
        d = _safe_date(int(m.group(3)), MONTH_INDEX.get(m.group(1)[:3].lower()), int(m.group(2)))
        if d and (best is None or m.start() < best[0]):
            best = (m.start(), d)
    for m in DATE_ISO.finditer(text):
        d = _safe_date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        if d and (best is None or m.start() < best[0]):
            best = (m.start(), d)
    return best[1] if best else None


def dated_rows(rows: list[dict] | None, today: date) -> list[dict]:
    """Deadline-like rows with a full date, earliest first; `passed` is true for dates before `today`."""
    out = []
    for r in rows or []:
        if not isinstance(r, dict):
            continue
        label, value = " ".join(str(r.get("label") or "").split()), " ".join(str(r.get("value") or "").split())
        d = first_date(value) if label and value else None
        if d is None or not DEADLINE_WORDS.search(f"{label} {value}"):
            continue
        out.append({"label": label, "value": value, "date": d, "passed": d < today})
    out.sort(key=lambda e: e["date"])   # stable: same-day rows keep the table's order
    return out


def deadline_timeline(rows: list[dict] | None, today: date) -> dict | None:
    """A proportional time axis with numbered dots (hollow once passed), a Today tick, year marks, and the numbered rows
    beneath with their values verbatim. None when fewer than two dated rows exist."""
    items = dated_rows(rows, today)
    if len(items) < 2:
        return None
    truncated, items = len(items) > MAX_DATES, items[:MAX_DATES]
    t0, t1 = min(items[0]["date"], today), max(items[-1]["date"], today)
    span = (t1 - t0).days
    ax0, ax1, axis_y = PAD + 10, W - PAD - 10, PAD + 26
    xpos = lambda d: (ax0 + (ax1 - ax0) * (d - t0).days / span) if span else (ax0 + ax1) / 2
    xs = [xpos(e["date"]) for e in items]
    gap = 20                                                      # numbered dots never overlap: push right, then back from the edge
    for i in range(1, len(xs)):
        xs[i] = max(xs[i], xs[i - 1] + gap)
    if xs[-1] > ax1:
        xs[-1] = ax1
        for i in range(len(xs) - 2, -1, -1):
            xs[i] = min(xs[i], xs[i + 1] - gap)
    parts = [f'<line x1="{ax0}" y1="{axis_y}" x2="{ax1}" y2="{axis_y}" stroke="{RULE_STRONG}" stroke-width="2"/>']
    years = False
    for yr in range(t0.year + 1, t1.year + 1):
        jan = date(yr, 1, 1)
        if t0 < jan <= t1:
            x = xpos(jan)
            parts.append(f'<line x1="{_n(x)}" y1="{axis_y}" x2="{_n(x)}" y2="{axis_y + 10}" stroke="{RULE_STRONG}" stroke-width="1"/>')
            parts.append(_text(x, axis_y + 22, str(yr), size=11, fill=INK_3, anchor="middle"))
            years = True
    tx = xpos(today)
    parts.append(f'<line x1="{_n(tx)}" y1="{axis_y - 12}" x2="{_n(tx)}" y2="{axis_y + 12}" stroke="{NAVY}" stroke-width="2"/>')
    parts.append(_text(tx, axis_y - 16, "Today", size=11, fill=NAVY, weight="700", anchor="middle" if 30 <= tx <= W - 30 else ("start" if tx < 30 else "end")))
    parts += [_badge(x, axis_y, i, passed=e["passed"]) for i, (e, x) in enumerate(zip(items, xs), 1)]
    y = axis_y + (38 if years else 26)
    x_text = PAD + 24
    for i, e in enumerate(items, 1):
        when = e["value"] if not e["passed"] or "passed" in e["value"].lower() else e["value"] + " (passed)"
        label_lines, when_lines = _wrap(e["label"], WRAP - 4, 3), _wrap(when, WRAP - 4, 2)
        parts.append(_badge(PAD + 8, y + 7, i, passed=e["passed"], r=8))
        parts.append(_lines(x_text, y + 12, label_lines, fill=INK_2))
        parts.append(_lines(x_text, y + 12 + len(label_lines) * LINE, when_lines, weight="700"))
        y += (len(label_lines) + len(when_lines)) * LINE + 10
    height = y - 10 + PAD
    title = "Deadlines and key dates"
    caption = f"Dates from the fact table above, earliest first. Dates before {date_text(today)}, when this page was built, are marked as passed."
    if truncated:
        caption += f" The first {MAX_DATES} such rows are shown."
    desc = "; ".join(f"{i}. {e['label']}: {e['value']}{' (passed)' if e['passed'] and 'passed' not in e['value'].lower() else ''}" for i, e in enumerate(items, 1))
    return {"kind": "timeline", "title": title, "svg": _svg("timeline", title, desc, height, "".join(parts)), "caption": caption}


# ------------------------------------------------------------------------------------------------ steps → numbered list
def steps_diagram(steps: list | None) -> dict | None:
    """A numbered vertical list of short step strings (at most six), wrapped, joined by a rule. None without steps."""
    items = []
    for s in steps or []:
        text = (s.get("text") or s.get("label")) if isinstance(s, dict) else s
        text = " ".join(str(text or "").split())
        if text:
            items.append(text)
    items = items[:MAX_STEPS]
    if not items:
        return None
    r = 11
    x_c, x_t = PAD + r, PAD + 2 * r + 12
    y, centers, texts = PAD, [], []
    for s in items:
        lines = _wrap(s, WRAP - 4, 4)
        centers.append(y + r)
        texts.append(_lines(x_t, y + 15, lines))
        y += max(len(lines) * LINE, 2 * r) + 14
    height = y - 14 + PAD
    rule = f'<line x1="{x_c}" y1="{centers[0]}" x2="{x_c}" y2="{centers[-1]}" stroke="{RULE_STRONG}" stroke-width="2"/>' if len(centers) > 1 else ""
    badges = "".join(_badge(x_c, cy, i, r=r) for i, cy in enumerate(centers, 1))
    title = "Step by step"
    desc = "; ".join(f"{i}. {s}" for i, s in enumerate(items, 1))
    return {"kind": "steps", "title": title, "svg": _svg("steps", title, desc, height, rule + "".join(texts) + badges), "caption": "The steps this guide gives, in order."}


# ------------------------------------------------------------------------------------------------ page → figures
def figures_for_page(page: dict, today: date) -> list[dict]:
    """Up to two figures the page's own data supports: a cost chart (two or more money rows on one billing period), a
    timeline (two or more dated deadline rows), a steps diagram (when the page carries `steps`), in that order."""
    rows = [r for r in (page.get("fact_table") or []) if isinstance(r, dict)]
    candidates = (cost_chart(rows), deadline_timeline(rows, today), steps_diagram(page.get("steps") or []))
    return [f for f in candidates if f][:2]


# ================================================================================================ v2 figure blocks (additive)
# A writer puts a fenced block with language `figure` in an article body (docs/v2/spec.md, contract 2). Its YAML is
# {kind: cost_table|timeline|steps, title, rows}; scripts/v2/render_site.py parses it and calls figure_from_block().
# Everything printed is the block's own text: the code only computes bar lengths and axis positions. The fact-table
# functions above are unchanged; these share their helpers and palette.
FIGURE_KINDS = ("cost_table", "timeline", "steps")
MAX_ROWS = 12


def _svg_u(uid: str, title: str, desc: str, height: float, body: str) -> str:
    """Like _svg(), with a caller-supplied id so two figures of one kind on a page never share ids."""
    h = int(round(height))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="100%" height="{h}" role="img" '
            f'aria-labelledby="{uid}-title" aria-describedby="{uid}-desc" font-size="13" style="font-family:{FONT};max-width:100%">'
            f'<title id="{uid}-title">{_t(title)}</title><desc id="{uid}-desc">{_t(desc)}</desc>{body}</svg>')


def _clean(s) -> str:
    return " ".join(str(s if s is not None else "").split())


def _block_rows(spec: dict) -> list[dict]:
    """Rows of a figure block with a non-empty label: {label, value, date}; a bare string row is a label."""
    out = []
    rows = spec.get("rows")
    for r in (rows if isinstance(rows, list) else [])[:MAX_ROWS]:
        row = {"label": _clean(r.get("label")), "value": r.get("value"), "date": r.get("date")} if isinstance(r, dict) else {"label": _clean(r), "value": None, "date": None}
        if row["label"]:
            out.append(row)
    return out


def _row_date(v) -> date | None:
    if isinstance(v, date):                      # a YAML date, or a datetime (a date subclass) when a time was given
        return v.date() if hasattr(v, "hour") else v
    return first_date(_clean(v)) if v else None


def cost_table_figure(spec: dict, uid: str = "fig-cost") -> dict | None:
    """`kind: cost_table`, rows {label, value}. Horizontal bars when every row carries a dollar amount (bars from zero, in the
    block's order, each row's own text beside its bar); otherwise a two-column table drawn in SVG. None without rows."""
    rows = [{"label": r["label"], "value": _clean(r["value"])} for r in _block_rows(spec)]
    if not rows:
        return None
    title = _clean(spec.get("title")) or "Costs"
    desc = "; ".join(f"{r['label']}: {r['value']}" for r in rows)
    money = money_rows(rows)
    if len(rows) >= 2 and len(money) == len(rows):
        full = all(len(m["value"]) <= FULL_VALUE_CHARS for m in money)
        printed = [m["value"] if full else m["amount_text"] for m in money]
        bar_max = max(120.0, W - 2 * PAD - (max(len(p) for p in printed) * 6.6 + 8))
        top = max(float(m["amount"]) for m in money)
        y, parts = PAD, []
        for m, p in zip(money, printed):
            lines = _wrap(m["label"], WRAP, 3)
            parts.append(_lines(PAD, y + 12, lines))
            y_bar = y + len(lines) * LINE + 3
            w = bar_max * float(m["amount"]) / top if top else 0.0
            parts.append(f'<rect x="{PAD}" y="{_n(y_bar)}" width="{_n(w)}" height="14" rx="2" fill="{NAVY}"><title>{_t(m["label"])}: {_t(m["value"])}</title></rect>')
            parts.append(_text(PAD + w + 6, y_bar + 11, p, weight="700"))
            y = y_bar + 28
        height = y - 14 + PAD
        axis = f'<line x1="{PAD}" y1="{PAD}" x2="{PAD}" y2="{_n(height - PAD)}" stroke="{RULE_STRONG}" stroke-width="1"/>'
        caption = "Bars start at zero." + ("" if full else " The number by each bar is the first dollar amount in that row; the basis is in the text.")
        return {"kind": "cost_table", "title": title, "svg": _svg_u(uid, title, desc, height, axis + "".join(parts)), "caption": caption}
    split = W * 0.52
    y, parts = PAD, []
    for r in rows:
        left, right = _wrap(r["label"], 24, 3), _wrap(r["value"] or "", 22, 3)
        parts.append(_lines(PAD, y + 12, left, fill=INK_2))
        parts.append(_lines(split, y + 12, right, weight="700"))
        y += max(len(left), len(right)) * LINE + 10
        parts.append(f'<line x1="{PAD}" y1="{_n(y - 4)}" x2="{W - PAD}" y2="{_n(y - 4)}" stroke="{RULE}" stroke-width="1"/>')
    parts.pop()
    return {"kind": "cost_table", "title": title, "svg": _svg_u(uid, title, desc, y - 10 + PAD, "".join(parts)), "caption": ""}


RULE = "var(--rule, #E3E0D8)"


def timeline_figure(spec: dict, uid: str = "fig-timeline", today: date | None = None) -> dict | None:
    """`kind: timeline`, rows {label, date}. When every date parses, the axis is proportional and sorted, with a Today tick and
    hollow badges for passed dates; otherwise rows keep their order, evenly spaced, and the date prints as written."""
    rows = _block_rows(spec)
    if not rows:
        return None
    today = today or date.today()
    title = _clean(spec.get("title")) or "Timeline"
    items = [{"label": r["label"], "date": _row_date(r["date"]), "text": _clean(r["date"]) if not isinstance(r["date"], date) else ""} for r in rows]
    for e in items:
        e["text"] = date_text(e["date"]) if e["date"] else e["text"]
        e["passed"] = bool(e["date"] and e["date"] < today)
    dated = all(e["date"] for e in items)
    ax0, ax1, axis_y = PAD + 10, W - PAD - 10, PAD + 26
    parts = [f'<line x1="{ax0}" y1="{axis_y}" x2="{ax1}" y2="{axis_y}" stroke="{RULE_STRONG}" stroke-width="2"/>']
    years = False
    if dated:
        items.sort(key=lambda e: e["date"])
        t0, t1 = min(items[0]["date"], today), max(items[-1]["date"], today)
        span = (t1 - t0).days
        xpos = lambda d: (ax0 + (ax1 - ax0) * (d - t0).days / span) if span else (ax0 + ax1) / 2
        xs = [xpos(e["date"]) for e in items]
        for i in range(1, len(xs)):
            xs[i] = max(xs[i], xs[i - 1] + 20)
        if xs[-1] > ax1:
            xs[-1] = ax1
            for i in range(len(xs) - 2, -1, -1):
                xs[i] = min(xs[i], xs[i + 1] - 20)
        for yr in range(t0.year + 1, t1.year + 1):
            jan = date(yr, 1, 1)
            if t0 < jan <= t1:
                x = xpos(jan)
                parts.append(f'<line x1="{_n(x)}" y1="{axis_y}" x2="{_n(x)}" y2="{axis_y + 10}" stroke="{RULE_STRONG}" stroke-width="1"/>')
                parts.append(_text(x, axis_y + 22, str(yr), size=11, fill=INK_3, anchor="middle"))
                years = True
        tx = xpos(today)
        parts.append(f'<line x1="{_n(tx)}" y1="{axis_y - 12}" x2="{_n(tx)}" y2="{axis_y + 12}" stroke="{NAVY}" stroke-width="2"/>')
        parts.append(_text(tx, axis_y - 16, "Today", size=11, fill=NAVY, weight="700", anchor="middle" if 30 <= tx <= W - 30 else ("start" if tx < 30 else "end")))
    else:
        n = len(items)
        xs = [ax0 + (ax1 - ax0) * k / (n - 1) if n > 1 else (ax0 + ax1) / 2 for k in range(n)]
    parts += [_badge(x, axis_y, i, passed=e["passed"]) for i, (e, x) in enumerate(zip(items, xs), 1)]
    y, x_text = axis_y + (38 if years else 26), PAD + 24
    for i, e in enumerate(items, 1):
        label_lines, when_lines = _wrap(e["label"], WRAP - 4, 3), _wrap(e["text"] + (" (passed)" if e["passed"] else ""), WRAP - 4, 2)
        parts.append(_badge(PAD + 8, y + 7, i, passed=e["passed"], r=8))
        parts.append(_lines(x_text, y + 12, label_lines, fill=INK_2))
        parts.append(_lines(x_text, y + 12 + len(label_lines) * LINE, when_lines, weight="700"))
        y += (len(label_lines) + len(when_lines)) * LINE + 10
    caption = f"Dates before {date_text(today)}, when this page was built, are marked as passed." if dated else "In the order the article gives them."
    desc = "; ".join(f"{i}. {e['label']}: {e['text']}" for i, e in enumerate(items, 1))
    return {"kind": "timeline", "title": title, "svg": _svg_u(uid, title, desc, y - 10 + PAD, "".join(parts)), "caption": caption}


def steps_figure(spec: dict, uid: str = "fig-steps") -> dict | None:
    """`kind: steps`, rows {label}: a numbered vertical list joined by a rule, the block's title on top. None without rows."""
    rows = _block_rows(spec)
    if not rows:
        return None
    title = _clean(spec.get("title")) or "Step by step"
    r = 11
    x_c, x_t = PAD + r, PAD + 2 * r + 12
    y, centers, texts = PAD, [], []
    for row in rows:
        lines = _wrap(row["label"], WRAP - 4, 4)
        centers.append(y + r)
        texts.append(_lines(x_t, y + 15, lines))
        y += max(len(lines) * LINE, 2 * r) + 14
    rule = f'<line x1="{x_c}" y1="{centers[0]}" x2="{x_c}" y2="{centers[-1]}" stroke="{RULE_STRONG}" stroke-width="2"/>' if len(centers) > 1 else ""
    badges = "".join(_badge(x_c, cy, i, r=r) for i, cy in enumerate(centers, 1))
    desc = "; ".join(f"{i}. {row['label']}" for i, row in enumerate(rows, 1))
    return {"kind": "steps", "title": title, "svg": _svg_u(uid, title, desc, y - 14 + PAD, rule + "".join(texts) + badges), "caption": ""}


def figure_from_block(spec: dict, uid: str = "fig", today: date | None = None) -> dict | None:
    """Dispatch a parsed ```figure block to its drawing: {kind, title, svg, caption}, or None for an unknown kind or no rows."""
    if not isinstance(spec, dict):
        return None
    kind = _clean(spec.get("kind"))
    if kind == "cost_table":
        return cost_table_figure(spec, uid)
    if kind == "timeline":
        return timeline_figure(spec, uid, today)
    if kind == "steps":
        return steps_figure(spec, uid)
    return None
