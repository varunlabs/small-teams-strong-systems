#!/usr/bin/env python3
"""Generate specific reference figures based on provided design sketches.

This repo stores rendered figures in manuscript/figures/generated and references
those images directly from the chapter markdown.

This script recreates (and overwrites):
- Figure 1.4 (ch01_why_big_teams_fig_1_4.png)
- Figure 2.1 (ch02_end_of_linear_scaling_fig_2_1.png)

No external assets are used; everything is drawn procedurally with PIL.
"""

from __future__ import annotations

from pathlib import Path
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "manuscript" / "figures" / "generated"


INK = (20, 24, 33)
SUBTLE = (110, 118, 130)
LIGHT = (230, 236, 245)
PAPER = (255, 255, 255)


def get_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates: list[str] = []
    if bold:
        candidates += [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/Library/Fonts/Arial Bold.ttf",
            "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf",
        ]
    candidates += [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttf",
    ]
    for p in candidates:
        try:
            return ImageFont.truetype(p, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def add_border(img: Image.Image) -> Image.Image:
    border = max(18, int(min(img.size) * 0.012))
    canvas = Image.new("RGB", (img.width + border * 2, img.height + border * 2), PAPER)
    canvas.paste(img, (border, border))
    d = ImageDraw.Draw(canvas)
    d.rectangle([0, 0, canvas.width - 1, canvas.height - 1], outline=LIGHT, width=3)
    return canvas


def _draw_person(d: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0):
    r = int(10 * scale)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=max(2, int(2 * scale)))
    body_w = int(22 * scale)
    body_h = int(28 * scale)
    d.rounded_rectangle(
        [cx - body_w // 2, cy + r - 2, cx + body_w // 2, cy + r - 2 + body_h],
        radius=int(7 * scale),
        outline=INK,
        width=max(2, int(2 * scale)),
    )


def _draw_bar_chart(d: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, level: float):
    d.rectangle([x, y, x + w, y + h], outline=SUBTLE, width=2)
    bars = 4
    gap = int(w * 0.08)
    bw = int((w - gap * (bars + 1)) / bars)
    max_h = int(h * (0.25 + 0.55 * level))
    for i in range(bars):
        bh = int(max_h * (0.45 + 0.55 * (i + 1) / bars))
        bx0 = x + gap + i * (bw + gap)
        by0 = y + h - bh - 6
        bx1 = bx0 + bw
        by1 = y + h - 6
        d.rectangle([bx0, by0, bx1, by1], fill=INK)


def _draw_gear(d: ImageDraw.ImageDraw, cx: int, cy: int, r: int):
    teeth = 10
    for t in range(teeth):
        ang = (2 * math.pi) * t / teeth
        x0 = cx + int(math.cos(ang) * (r + 3))
        y0 = cy + int(math.sin(ang) * (r + 3))
        x1 = cx + int(math.cos(ang) * (r + 10))
        y1 = cy + int(math.sin(ang) * (r + 10))
        d.line([(x0, y0), (x1, y1)], fill=INK, width=3)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=3)
    d.ellipse([cx - r // 3, cy - r // 3, cx + r // 3, cy + r // 3], outline=INK, width=3)


def _draw_org_chart(d: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int):
    box = int(min(w, h) * 0.18)
    top = [x + (w - box) // 2, y, x + (w + box) // 2, y + box]
    left = [x + int(w * 0.14), y + int(h * 0.52), x + int(w * 0.14) + box, y + int(h * 0.52) + box]
    mid = [x + (w - box) // 2, y + int(h * 0.52), x + (w + box) // 2, y + int(h * 0.52) + box]
    right = [x + int(w * 0.86) - box, y + int(h * 0.52), x + int(w * 0.86), y + int(h * 0.52) + box]

    for rect in (top, left, mid, right):
        d.rounded_rectangle(rect, radius=10, outline=INK, width=3)

    tx = (top[0] + top[2]) // 2
    ty = top[3]
    my = left[1]
    d.line([(tx, ty), (tx, my - 10)], fill=INK, width=3)
    d.line([(left[0] + box // 2, my - 10), (right[0] + box // 2, my - 10)], fill=INK, width=3)

    for rect in (left, mid, right):
        cx = (rect[0] + rect[2]) // 2
        d.line([(cx, my - 10), (cx, rect[1])], fill=INK, width=3)


def _draw_venn(d: ImageDraw.ImageDraw, cx: int, cy: int, r: int):
    for dx, dy in [(-r // 2, 0), (r // 2, 0), (0, r // 2)]:
        d.ellipse([cx + dx - r, cy + dy - r, cx + dx + r, cy + dy + r], outline=INK, width=3)


def generate_figure_2_1(path: Path):
    w, h = 1800, 900
    img = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(img)

    title_font = get_font(42, bold=True)
    label_font = get_font(40, bold=False)

    margin_x = 120
    top = 120
    col_w = int((w - margin_x * 2) / 3)

    centers = [margin_x + col_w // 2, margin_x + col_w + col_w // 2, margin_x + 2 * col_w + col_w // 2]

    # Arrows between columns.
    for i in range(2):
        x0 = margin_x + (i + 1) * col_w - 60
        x1 = x0 + 120
        y = top + 120
        d.line([(x0, y), (x1, y)], fill=INK, width=6)
        d.polygon([(x1, y), (x1 - 22, y - 16), (x1 - 22, y + 16)], fill=INK)

    # Column 1: small team + basic output.
    x = centers[0]
    for dx in (-50, 0, 50):
        _draw_person(d, x + dx, top + 70, scale=1.0)
    _draw_bar_chart(d, x - 140, top + 240, 280, 180, level=0.35)
    d.text((x - 160, top + 460), "Initial Output", font=label_font, fill=INK)

    # Column 2: bigger team + gears + higher output.
    x = centers[1]
    for dx in (-70, -20, 30, 80, 130):
        _draw_person(d, x + dx, top + 70, scale=1.0)
    _draw_gear(d, x - 30, top + 165, 30)
    _draw_gear(d, x + 55, top + 170, 22)
    _draw_bar_chart(d, x - 140, top + 240, 280, 180, level=0.65)
    d.text((x - 190, top + 460), "Increased Output", font=label_font, fill=INK)

    # Column 3: hierarchy + complexity + output.
    x = centers[2]
    _draw_org_chart(d, x - 180, top + 20, 360, 220)
    _draw_venn(d, x, top + 330, 70)
    _draw_bar_chart(d, x - 140, top + 520, 280, 180, level=0.85)
    d.text((x - 175, top + 745), "Expanded Output", font=label_font, fill=INK)

    # Light baseline guides (subtle).
    d.line([(margin_x, top + 690), (w - margin_x, top + 690)], fill=LIGHT, width=3)

    img = add_border(img)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG", optimize=True)


def generate_figure_1_4(path: Path):
    w, h = 1800, 800
    img = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(img)

    font = get_font(34)
    font_b = get_font(34, bold=True)

    left = 160
    right = 120
    top = 120
    bottom = 150

    x0, y0 = left, h - bottom
    x1, y1 = w - right, top

    # Axes
    d.line([(x0, y0), (x0, y1)], fill=INK, width=4)
    d.line([(x0, y0), (x1, y0)], fill=INK, width=4)
    d.polygon([(x0, y1), (x0 - 12, y1 + 20), (x0 + 12, y1 + 20)], fill=INK)
    d.polygon([(x1, y0), (x1 - 20, y0 - 12), (x1 - 20, y0 + 12)], fill=INK)

    # Curve: rise -> peak -> slow decline.
    pts = []
    for i in range(0, 220):
        t = i / 219
        # A smooth bump with a later decline.
        y = 0.35 + 0.55 * math.sin(min(math.pi, t * 1.1))
        y -= 0.22 * max(0.0, (t - 0.58)) ** 0.8
        x = t
        px = int(x0 + x * (x1 - x0))
        py = int(y0 - y * (y0 - y1) * 0.82)
        pts.append((px, py))
    d.line(pts, fill=INK, width=5, joint="curve")

    # Environmental shift marker.
    shift_t = 0.58
    sx = int(x0 + shift_t * (x1 - x0))
    d.line([(sx, y1 + 10), (sx, y0 - 10)], fill=SUBTLE, width=4)

    label = "Environmental shift"
    bbox = d.textbbox((0, 0), label, font=font)
    tw = bbox[2] - bbox[0]
    d.text((sx - tw // 2, y1 - 55), label, font=font, fill=INK)

    # Axis labels.
    d.text((x0 - 150, (y0 + y1) // 2 - 10), "Large-Team\nEffectiveness", font=font, fill=INK, align="center")
    d.text(((x0 + x1) // 2 - 30, y0 + 50), "Time", font=font_b, fill=INK)

    # Region labels.
    d.text((x0 + 220, y0 + 15), "Prior Constraints", font=font, fill=SUBTLE)
    d.text((sx + 140, y0 + 15), "New Conditions", font=font, fill=SUBTLE)

    img = add_border(img)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG", optimize=True)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    generate_figure_1_4(OUT_DIR / "ch01_why_big_teams_fig_1_4.png")
    generate_figure_2_1(OUT_DIR / "ch02_end_of_linear_scaling_fig_2_1.png")

    print("generated", OUT_DIR / "ch01_why_big_teams_fig_1_4.png")
    print("generated", OUT_DIR / "ch02_end_of_linear_scaling_fig_2_1.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
