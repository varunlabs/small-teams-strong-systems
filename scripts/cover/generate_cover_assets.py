#!/usr/bin/env python3
from __future__ import annotations

import math
from pathlib import Path
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "manuscript" / "cover"
OUT.mkdir(parents=True, exist_ok=True)

# KDP A5 cover panels in the wrap generator are sized to TRIM + BLEED.
TRIM_W_IN = 5.83
TRIM_H_IN = 8.27
BLEED_IN = 0.125
DPI = 300

W_TRIM = int(round(TRIM_W_IN * DPI))
H_TRIM = int(round(TRIM_H_IN * DPI))

W_BLEED = int(round((TRIM_W_IN + BLEED_IN) * DPI))
H_BLEED = int(round((TRIM_H_IN + 2 * BLEED_IN) * DPI))


def get_font(size: int, bold: bool = False):
    candidates = []
    if bold:
        candidates += [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/Library/Fonts/Arial Bold.ttf",
            "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
        ]
    candidates += [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def vertical_gradient(size: tuple[int, int], top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    w, h = size
    base = Image.new("RGB", (w, h), top)
    draw = ImageDraw.Draw(base)
    for y in range(h):
        t = y / max(1, h - 1)
        r = int(top[0] * (1 - t) + bottom[0] * t)
        g = int(top[1] * (1 - t) + bottom[1] * t)
        b = int(top[2] * (1 - t) + bottom[2] * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return base.convert("RGBA")


def film_grain(size: tuple[int, int], amount: int = 18, seed: int = 17) -> Image.Image:
    rng = random.Random(seed)
    w, h = size
    noise = Image.new("L", (w, h))
    px = noise.load()
    for y in range(h):
        for x in range(w):
            px[x, y] = 128 + rng.randint(-amount, amount)
    noise = noise.filter(ImageFilter.GaussianBlur(radius=0.8))
    return noise


def add_soft_light_orbs(img: Image.Image, seed: int) -> Image.Image:
    w, h = img.size
    rng = random.Random(seed)
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    palette = [
        (122, 208, 255, 120),
        (154, 145, 255, 105),
        (127, 255, 218, 95),
        (255, 160, 198, 70),
    ]
    for _ in range(14):
        radius = int(rng.uniform(0.08, 0.22) * min(w, h))
        cx = int(rng.uniform(0.08, 0.92) * w)
        cy = int(rng.uniform(0.05, 0.95) * h)
        col = palette[rng.randrange(len(palette))]
        d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=col)
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=70))
    return Image.alpha_composite(img, overlay)


def add_wave_lines(img: Image.Image, color: tuple[int, int, int], alpha: int) -> Image.Image:
    w, h = img.size
    lines = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lines)

    for band in range(10):
        y_base = int(h * (0.18 + 0.075 * band))
        amp = int(h * (0.02 + band * 0.0015))
        phase = band * 0.55
        pts: list[tuple[int, int]] = []
        for x in range(0, w, 8):
            y = y_base + int(amp * math.sin((x / w) * math.pi * 3.2 + phase))
            pts.append((x, y))
        d.line(pts, fill=(color[0], color[1], color[2], max(40, alpha - band * 5)), width=2)

    lines = lines.filter(ImageFilter.GaussianBlur(radius=0.7))
    return Image.alpha_composite(img, lines)


def add_glass_panel(img: Image.Image, box: tuple[int, int, int, int]) -> Image.Image:
    panel = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(panel)
    x0, y0, x1, y1 = box
    d.rounded_rectangle([x0, y0, x1, y1], radius=42, fill=(14, 24, 43, 132), outline=(185, 223, 255, 108), width=2)
    d.rounded_rectangle([x0 + 12, y0 + 12, x1 - 12, y0 + 68], radius=28, fill=(255, 255, 255, 20))
    return Image.alpha_composite(img, panel)


def modern_cover_bg(size: tuple[int, int], seed: int) -> Image.Image:
    base = vertical_gradient(size, (9, 15, 33), (28, 46, 86))
    base = add_soft_light_orbs(base, seed=seed)
    base = add_wave_lines(base, color=(169, 227, 255), alpha=110)
    grain = film_grain(size, amount=16, seed=seed + 100)
    grain_rgb = Image.merge("RGBA", (grain, grain, grain, Image.new("L", size, 24)))
    base = Image.alpha_composite(base, grain_rgb)
    return base.filter(ImageFilter.UnsharpMask(radius=1.6, percent=110, threshold=3)).convert("RGB")


def draw_text_with_shadow(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font: ImageFont.ImageFont,
                          fill: tuple[int, int, int], shadow: tuple[int, int, int] = (0, 0, 0),
                          offset: tuple[int, int] = (2, 2), shadow_alpha: int = 120):
    x, y = xy
    # PIL doesn't support alpha in RGB mode, so shadow_alpha just controls darkness via blend.
    sx, sy = offset
    draw.text((x + sx, y + sy), text, font=font, fill=tuple(int(c * (shadow_alpha / 255)) for c in shadow))
    draw.text((x, y), text, font=font, fill=fill)


def front_cover() -> Image.Image:
    bg = modern_cover_bg((W_BLEED, H_BLEED), seed=101).convert("RGBA")
    bg = add_glass_panel(bg, (
        int(W_BLEED * 0.05),
        int(H_BLEED * 0.08),
        int(W_BLEED * 0.95),
        int(H_BLEED * 0.93),
    ))
    img = bg.convert("RGB")
    d = ImageDraw.Draw(img)

    title_font = get_font(108, bold=True)
    subtitle_font = get_font(48)
    small_font = get_font(34)
    quote_font = get_font(36)
    author_font = get_font(50, bold=True)

    left = int(W_BLEED * 0.10)
    top = int(H_BLEED * 0.16)

    draw_text_with_shadow(d, (left, top), "SMALL TEAMS", title_font, (245, 250, 255), offset=(3, 3), shadow_alpha=150)
    draw_text_with_shadow(d, (left, top + 136), "STRONG SYSTEMS", title_font, (245, 250, 255), offset=(3, 3), shadow_alpha=150)
    d.text((left, top + 292), "Designing High-Leverage Work for Strong Systems", font=subtitle_font, fill=(214, 236, 255))
    d.line([(left, top + 412), (W_BLEED - left, top + 412)], fill=(150, 221, 255), width=3)

    d.text((left, top + 500), "A practical guide for founders, builders, researchers,", font=small_font, fill=(226, 239, 255))
    d.text((left, top + 552), "and managers designing high-leverage teams.", font=small_font, fill=(226, 239, 255))

    pill_y = top + 680
    d.rounded_rectangle([left - 12, pill_y, W_BLEED - left + 12, pill_y + 98], radius=22, fill=(18, 36, 62), outline=(140, 213, 255), width=2)
    d.text((left + 10, pill_y + 28), "Execution is abundant. Judgment is the bottleneck.", font=quote_font, fill=(232, 244, 255))

    d.text((left, int(H_BLEED * 0.91)), "VARUN KUMAR SIDDARAJU", font=author_font, fill=(245, 250, 255))
    return img


def back_cover() -> Image.Image:
    bg = modern_cover_bg((W_BLEED, H_BLEED), seed=202).convert("RGBA")
    bg = add_glass_panel(bg, (
        int(W_BLEED * 0.06),
        int(H_BLEED * 0.10),
        int(W_BLEED * 0.94),
        int(H_BLEED * 0.92),
    ))
    img = bg.convert("RGB")
    d = ImageDraw.Draw(img)

    h_font = get_font(56, bold=True)
    body_font = get_font(37)

    left = int(W_BLEED * 0.10)
    y = int(H_BLEED * 0.18)
    draw_text_with_shadow(d, (left, y), "What if growth no longer required headcount?", h_font, (245, 250, 255), offset=(3, 3), shadow_alpha=155)

    lines = [
        "In an AI-amplified world, execution is abundant.",
        "The real bottleneck is judgment, structure, and decision integrity.",
        "",
        "Small Teams, Strong Systems presents a practical operating model",
        "for building complex products with fewer people and more leverage.",
        "",
        "Inside, you will find:",
        "- A 6-person operating model for high-leverage execution",
        "- Structural patterns that prevent bloat and burnout",
        "- Decision systems for uncertainty and frontier complexity",
        "- Practical examples from technology, product, and research teams",
    ]

    y = int(H_BLEED * 0.30)
    for line in lines:
        d.text((left, y), line, font=body_font, fill=(227, 241, 255))
        y += 58

    bx0 = int(W_BLEED * 0.10)
    by0 = int(H_BLEED * 0.84)
    bx1 = int(W_BLEED * 0.46)
    by1 = int(H_BLEED * 0.96)
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=14, fill=(245, 250, 255))
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=14, outline=(199, 220, 239), width=3)
    return img


def editorial_variant_bg(size: tuple[int, int], top: tuple[int, int, int], bottom: tuple[int, int, int], seed: int) -> Image.Image:
    base = vertical_gradient(size, top, bottom).convert("RGBA")
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    w, h = size

    d.rectangle([int(w * 0.06), int(h * 0.12), int(w * 0.93), int(h * 0.88)], fill=(255, 255, 255, 26))
    d.rectangle([int(w * 0.09), int(h * 0.15), int(w * 0.90), int(h * 0.85)], outline=(255, 255, 255, 72), width=3)

    accent_colors = [
        (250, 208, 120, 135),
        (255, 168, 124, 118),
        (160, 199, 255, 112),
    ]
    for idx, color in enumerate(accent_colors):
        y = int(h * (0.24 + idx * 0.18))
        d.rounded_rectangle([int(w * 0.13), y, int(w * 0.87), y + int(h * 0.055)], radius=28, fill=color)

    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=1.1))
    base = Image.alpha_composite(base, overlay)
    grain = film_grain(size, amount=14, seed=seed)
    grain_rgb = Image.merge("RGBA", (grain, grain, grain, Image.new("L", size, 18)))
    return Image.alpha_composite(base, grain_rgb).convert("RGB")


def front_cover_option2() -> Image.Image:
    img = editorial_variant_bg((W_BLEED, H_BLEED), (28, 30, 55), (54, 68, 96), seed=303)
    d = ImageDraw.Draw(img)

    title_font = get_font(102, bold=True)
    subtitle_font = get_font(44)
    body_font = get_font(33)
    author_font = get_font(48, bold=True)

    left = int(W_BLEED * 0.12)
    top = int(H_BLEED * 0.19)

    d.text((left, top), "SMALL TEAMS", font=title_font, fill=(246, 247, 255))
    d.text((left, top + 126), "STRONG SYSTEMS", font=title_font, fill=(246, 247, 255))
    d.text((left, top + 276), "Designing High-Leverage Work for Strong Systems", font=subtitle_font, fill=(230, 236, 255))

    d.line([(left, top + 364), (W_BLEED - left, top + 364)], fill=(255, 196, 126), width=4)
    d.text((left, top + 430), "A clear operating model for building more with fewer people.", font=body_font, fill=(234, 238, 255))
    d.text((left, top + 480), "Simple structure. Strong judgment. Sustainable speed.", font=body_font, fill=(234, 238, 255))

    tag_y = int(H_BLEED * 0.77)
    d.rounded_rectangle([left - 8, tag_y, W_BLEED - left + 8, tag_y + 92], radius=18, fill=(25, 29, 47), outline=(255, 196, 126), width=2)
    d.text((left + 18, tag_y + 28), "Execution is cheap. Coherence is rare.", font=get_font(36), fill=(251, 239, 224))

    d.text((left, int(H_BLEED * 0.91)), "VARUN KUMAR SIDDARAJU", font=author_font, fill=(246, 247, 255))
    return img


def back_cover_option2() -> Image.Image:
    img = editorial_variant_bg((W_BLEED, H_BLEED), (34, 37, 63), (63, 81, 112), seed=404)
    d = ImageDraw.Draw(img)

    h_font = get_font(52, bold=True)
    body_font = get_font(35)

    left = int(W_BLEED * 0.11)
    y = int(H_BLEED * 0.17)
    d.text((left, y), "Build leverage, not bureaucracy.", font=h_font, fill=(247, 248, 255))

    lines = [
        "This book explains how high-performing teams stay small",
        "while handling complex product and research work.",
        "",
        "You will learn:",
        "- Why six is a powerful team design constraint",
        "- How to separate judgment from routine execution",
        "- How to design systems that scale without managerial bloat",
        "- How leaders preserve coherence under pressure",
    ]

    y = int(H_BLEED * 0.30)
    for line in lines:
        d.text((left, y), line, font=body_font, fill=(233, 238, 255))
        y += 57

    bx0 = int(W_BLEED * 0.11)
    by0 = int(H_BLEED * 0.84)
    bx1 = int(W_BLEED * 0.46)
    by1 = int(H_BLEED * 0.96)
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=14, fill=(247, 248, 255))
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=14, outline=(214, 219, 236), width=3)
    return img


front = front_cover()
back = back_cover()
front_option2 = front_cover_option2()
back_option2 = back_cover_option2()

front.save(OUT / "cover_front.png")
back.save(OUT / "cover_back.png")
front_option2.save(OUT / "cover_front_option2.png")
back_option2.save(OUT / "cover_back_option2.png")

# Also generate trim-sized versions (no bleed) for embedding into PDFs/DOCX/EPUB.
# The bleed versions are still used for KDP wrap cover generation.
front_trim = ImageOps.fit(front, (W_TRIM, H_TRIM), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
back_trim = ImageOps.fit(back, (W_TRIM, H_TRIM), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
front_trim_option2 = ImageOps.fit(front_option2, (W_TRIM, H_TRIM), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
back_trim_option2 = ImageOps.fit(back_option2, (W_TRIM, H_TRIM), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
front_trim.save(OUT / "cover_front_trim.png")
back_trim.save(OUT / "cover_back_trim.png")
front_trim_option2.save(OUT / "cover_front_option2_trim.png")
back_trim_option2.save(OUT / "cover_back_option2_trim.png")

print("generated", OUT / "cover_front.png")
print("generated", OUT / "cover_back.png")
print("generated", OUT / "cover_front_trim.png")
print("generated", OUT / "cover_back_trim.png")
print("generated", OUT / "cover_front_option2.png")
print("generated", OUT / "cover_back_option2.png")
print("generated", OUT / "cover_front_option2_trim.png")
print("generated", OUT / "cover_back_option2_trim.png")
