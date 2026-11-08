#!/usr/bin/env python3
"""Generate clearly labeled SYNTHETIC placeholder illustrations for the preview site.

    worker/.venv/bin/python scripts/make_placeholders.py

Flat, deterministic vector-style compositions (no photography, no model-generated imagery) drawn with
Pillow, written to worker/campus_worker/render/static/img/placeholders/. Every image carries a
"Synthetic placeholder" mark; real pages must use rights-cleared photography with a credit line.
"""
from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parents[1] / "worker" / "campus_worker" / "render" / "static" / "img" / "placeholders"
W, H = 1600, 1000
PAPER = (250, 249, 246)
SKY = [(228, 234, 231), (236, 232, 222), (223, 230, 236)]
BRICK = [(166, 98, 76), (191, 128, 96), (140, 92, 78)]
STONE = [(205, 198, 182), (186, 180, 166), (221, 214, 198)]
GREEN = [(63, 110, 92), (86, 134, 110), (47, 93, 80)]
INK = (23, 23, 23)
LABEL = (87, 87, 87)


def font(size: int) -> ImageFont.ImageFont:
    for p in ("/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/Supplemental/Arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def building(d: ImageDraw.ImageDraw, x: int, ground: int, w: int, h: int, color, rng: random.Random, tower: bool = False) -> None:
    d.rectangle([x, ground - h, x + w, ground], fill=color)
    # cornice band
    d.rectangle([x, ground - h, x + w, ground - h + 14], fill=tuple(max(0, c - 28) for c in color))
    if tower:
        tw = w // 4
        d.rectangle([x + w // 2 - tw // 2, ground - h - 120, x + w // 2 + tw // 2, ground - h], fill=color)
        d.polygon([(x + w // 2 - tw // 2 - 8, ground - h - 120), (x + w // 2, ground - h - 190), (x + w // 2 + tw // 2 + 8, ground - h - 120)], fill=tuple(max(0, c - 40) for c in color))
    # windows
    cols = max(2, w // 70)
    rows = max(2, (h - 60) // 80)
    cw, ch = 26, 40
    gx = (w - cols * cw) / (cols + 1)
    gy = (h - 50 - rows * ch) / (rows + 1)
    for r in range(rows):
        for c in range(cols):
            wx = x + gx + c * (cw + gx)
            wy = ground - h + 30 + gy + r * (ch + gy)
            lit = rng.random() < 0.18
            d.rectangle([wx, wy, wx + cw, wy + ch], fill=(244, 232, 196) if lit else (236, 240, 240))
            d.rectangle([wx, wy, wx + cw, wy + ch], outline=tuple(max(0, c2 - 50) for c2 in color), width=2)
    # door
    dw = 44
    d.rectangle([x + w // 2 - dw // 2, ground - 70, x + w // 2 + dw // 2, ground], fill=tuple(max(0, c - 60) for c in color))


def tree(d: ImageDraw.ImageDraw, x: int, ground: int, s: int, color) -> None:
    d.rectangle([x - s // 12, ground - s // 2, x + s // 12, ground], fill=(110, 84, 64))
    d.ellipse([x - s // 2, ground - s - s // 4, x + s // 2, ground - s // 4], fill=color)
    d.ellipse([x - s // 3, ground - s - s // 2, x + s // 3, ground - s // 2], fill=tuple(min(255, c + 18) for c in color))


def compose(name: str, seed: int, kind: str) -> None:
    rng = random.Random(seed)
    im = Image.new("RGB", (W, H), rng.choice(SKY))
    d = ImageDraw.Draw(im)
    ground = int(H * 0.74)
    # ground
    d.rectangle([0, ground, W, H], fill=(214, 212, 196))
    d.rectangle([0, ground, W, ground + 10], fill=(190, 188, 172))
    # lawn + path
    d.rectangle([0, ground + 10, W, H], fill=(196, 206, 180))
    d.polygon([(W * 0.42, H), (W * 0.58, H), (W * 0.53, ground + 10), (W * 0.47, ground + 10)], fill=(222, 216, 196))
    # distant hills
    d.ellipse([-300, ground - 160, W * 0.6, ground + 60], fill=(205, 212, 200))
    d.ellipse([W * 0.45, ground - 120, W + 300, ground + 60], fill=(196, 206, 194))
    palette = {"hall": BRICK, "quad": STONE, "campus": BRICK + STONE, "library": STONE}[kind]
    x = 60
    n = {"hall": 1, "quad": 3, "campus": 5, "library": 2}[kind]
    if kind == "hall":
        building(d, 300, ground, 1000, 520, rng.choice(BRICK), rng)
        tree(d, 150, ground + 20, 220, rng.choice(GREEN)); tree(d, 1460, ground + 30, 260, rng.choice(GREEN))
    else:
        widths = [rng.randint(180, 340) for _ in range(n)]
        total = sum(widths) + 50 * (n - 1)
        x = (W - total) // 2
        for i, w in enumerate(widths):
            h = rng.randint(260, 520)
            building(d, x, ground, w, h, rng.choice(palette), rng, tower=(i == n // 2 and kind != "quad"))
            x += w + 50
        for tx in (90, 330, W - 120, W - 380):
            tree(d, tx, ground + rng.randint(10, 40), rng.randint(150, 240), rng.choice(GREEN))
    # label
    f = font(26)
    text = "Synthetic placeholder illustration — not a real campus"
    tw = d.textlength(text, font=f)
    d.rectangle([W - tw - 48, H - 64, W, H], fill=PAPER)
    d.text((W - tw - 24, H - 48), text, fill=LABEL, font=f)
    OUT.mkdir(parents=True, exist_ok=True)
    im.save(OUT / f"{name}.jpg", quality=82, optimize=True)
    im.resize((800, 500), Image.LANCZOS).save(OUT / f"{name}-800.jpg", quality=80, optimize=True)
    print("wrote", name)


if __name__ == "__main__":
    compose("fixture-hall", 11, "hall")
    compose("riverside-hall", 23, "hall")
    compose("fixture-state-campus", 37, "campus")
    compose("quad", 41, "quad")
    compose("library", 53, "library")
