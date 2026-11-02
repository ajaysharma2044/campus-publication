#!/usr/bin/env python3
"""Contrast and token checks for the design system (SPEC §04, §31).

Computes WCAG 2.x contrast for every text/background pairing the templates actually use and
fails if any normal-text pair is below 4.5:1 (3:1 for the large masthead). Also verifies the CSS
contains no forbidden decoration (gradient heroes, blur/glass, border-radius pills) outside the
one allowed skeleton shimmer.
"""
import re
import sys
from pathlib import Path

CSS = Path(__file__).resolve().parents[1] / "worker" / "campus_worker" / "render" / "static" / "campus.css"


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def lum(rgb):
    def ch(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = lum(hex_to_rgb(a)), lum(hex_to_rgb(b))
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def main() -> int:
    css = CSS.read_text()
    tokens = dict(re.findall(r"--([a-z0-9-]+):\s*(#[0-9A-Fa-f]{6})", css))
    pairs = [
        ("ink", "paper", 4.5, "body text on paper"), ("ink", "surface", 4.5, "body text on surface"),
        ("ink-2", "paper", 4.5, "secondary text on paper"), ("ink-2", "surface", 4.5, "secondary on surface"),
        ("ink-3", "paper", 4.5, "metadata on paper"), ("ink-3", "surface", 4.5, "metadata on surface"),
        ("navy", "paper", 4.5, "links on paper"), ("navy", "surface", 4.5, "links on surface"), ("navy", "navy-wash", 4.5, "navy text on wash"),
        ("warn-ink", "paper", 4.5, "stale notice text"), ("warn-ink", "warn-wash", 4.5, "stale notice on wash"),
        ("ok-ink", "surface", 4.5, "verified tag"), ("ink-2", "surface", 4.5, "sponsored label"),
    ]
    extra = [("#FFFFFF", tokens["navy"], 4.5, "button text on navy"), ("#FFFFFF", tokens["ink"], 4.5, "consent bar text on ink"), ("#8A1C1C", tokens["surface"], 4.5, "error text")]
    failures = []
    print(f"{'pair':40s} {'ratio':>6s}  min")
    for a, b, mn, label in pairs:
        r = contrast(tokens[a], tokens[b])
        print(f"{label:40s} {r:6.2f}  {mn}{'  FAIL' if r < mn else ''}")
        if r < mn:
            failures.append(label)
    for a, b, mn, label in extra:
        r = contrast(a, b)
        print(f"{label:40s} {r:6.2f}  {mn}{'  FAIL' if r < mn else ''}")
        if r < mn:
            failures.append(label)
    # forbidden decoration
    body = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    gradients = [m for m in re.finditer(r"linear-gradient|radial-gradient", body)]
    allowed_gradients = len(re.findall(r"\.skeleton \{[^}]*linear-gradient", body))
    if len(gradients) > allowed_gradients:
        failures.append("gradient outside skeleton shimmer")
    if re.search(r"backdrop-filter|blur\(", body):
        failures.append("glass/blur effect present")
    big_radius = [m.group(0) for m in re.finditer(r"border-radius:\s*(\d+)px", body) if int(m.group(1)) > 4]
    if big_radius:
        failures.append(f"large border-radius: {big_radius}")
    if re.search(r"text-align:\s*justify", body):
        failures.append("justified text")
    print("\nforbidden-decoration check:", "FAIL " + str(failures) if failures else "ok")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
