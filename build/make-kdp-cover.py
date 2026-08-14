#!/usr/bin/env python3
"""Build a KDP paperback print cover: back panel + spine + front panel, one
full-wrap PDF at the exact dimensions KDP requires for the given page count.

Formula used (KDP paperback, black & white interior, white paper):
    spine_width_in = page_count * 0.002252
    full_width_in  = bleed + trim_w + spine_width_in + trim_w + bleed
    full_height_in = bleed + trim_h + bleed
    bleed = 0.125in on every outer edge (not on the spine seams)

The existing front/back cover art (published/v1/cover_front.jpg,
cover_back.png) is only 1024x1536px -- below true 300dpi for a 6x9in trim
panel with bleed (which needs ~1838x2775px). It is upscaled with high-quality
resampling to fill the panel; this will look slightly softer in print than on
a Kindle thumbnail, not pixelated, but not pin-sharp either. Flag this to the
user rather than hide it.

Usage: make-kdp-cover.py <page_count> <front.jpg> <back.png> <gelasio-bold.ttf> <out.pdf>
"""
import sys
from PIL import Image, ImageDraw, ImageFont

page_count, front_path, back_path, font_path, out_path = sys.argv[1:6]
page_count = int(page_count)

DPI = 300
BLEED_IN = 0.125
TRIM_W_IN, TRIM_H_IN = 6.0, 9.0
SPINE_IN = page_count * 0.002252

FULL_W_IN = BLEED_IN + TRIM_W_IN + SPINE_IN + TRIM_W_IN + BLEED_IN
FULL_H_IN = BLEED_IN + TRIM_H_IN + BLEED_IN

px = lambda inches: round(inches * DPI)
FULL_W, FULL_H = px(FULL_W_IN), px(FULL_H_IN)
BLEED = px(BLEED_IN)
PANEL_W = px(BLEED_IN + TRIM_W_IN)  # back/front panel including its outer bleed edge
SPINE_W = px(SPINE_IN)

print(f"page_count={page_count} spine={SPINE_IN:.4f}in "
      f"full={FULL_W_IN:.4f}x{FULL_H_IN:.4f}in ({FULL_W}x{FULL_H}px @ {DPI}dpi)")

canvas = Image.new("RGB", (FULL_W, FULL_H), "white")


def fit_panel(img_path, panel_w, panel_h):
    """Scale + center-crop source art to exactly fill a panel (cover, not
    contain), matching how a bleed-safe cover panel is normally prepared."""
    im = Image.open(img_path).convert("RGB")
    src_w, src_h = im.size
    scale = max(panel_w / src_w, panel_h / src_h)
    new_w, new_h = round(src_w * scale), round(src_h * scale)
    im = im.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - panel_w) // 2
    top = (new_h - panel_h) // 2
    return im.crop((left, top, left + panel_w, top + panel_h))


# Back cover: occupies x=[0, PANEL_W)
back = fit_panel(back_path, PANEL_W, FULL_H)
canvas.paste(back, (0, 0))

# Front cover: occupies x=[PANEL_W + SPINE_W, FULL_W)
front = fit_panel(front_path, PANEL_W, FULL_H)
canvas.paste(front, (FULL_W - PANEL_W, 0))

# Spine: occupies x=[PANEL_W, PANEL_W + SPINE_W)
spine_x0 = PANEL_W
spine = Image.new("RGB", (SPINE_W, FULL_H), "#f7f5f1")  # matches the cover's off-white
draw = ImageDraw.Draw(spine)

title = "SMALL TEAMS, STRONG SYSTEMS"
author = "VARUN KUMAR SIDDARAJU"
title_size = max(20, min(34, SPINE_W // 8))
author_size = max(14, round(title_size * 0.62))
title_font = ImageFont.truetype(font_path, title_size)
author_font = ImageFont.truetype(font_path, author_size)

# Render title/author on a separate transparent strip, then rotate 90 deg so
# they read top-to-bottom on the spine (standard convention for spines this
# narrow). Strip length = spine's usable print length (full height minus a
# safe margin from each bleed edge); strip thickness = spine width minus a
# small inset from each spine seam.
inset = max(6, SPINE_W // 20)
strip_h = SPINE_W - 2 * inset
strip_w = FULL_H - 2 * BLEED
strip = Image.new("RGBA", (strip_w, strip_h), (0, 0, 0, 0))
sdraw = ImageDraw.Draw(strip)

title_color = "#1a2b4a"   # dark navy, matches the front cover's title color
author_color = "#5a6b7a"  # muted blue-gray, matches the front cover's subtitle color

tb = sdraw.textbbox((0, 0), title, font=title_font)
tw, th = tb[2] - tb[0], tb[3] - tb[1]
sdraw.text(((strip_w - tw) / 2, (strip_h - th) / 2 - strip_h * 0.16 - tb[1]),
           title, font=title_font, fill=title_color)

ab = sdraw.textbbox((0, 0), author, font=author_font)
aw, ah = ab[2] - ab[0], ab[3] - ab[1]
sdraw.text(((strip_w - aw) / 2, (strip_h - ah) / 2 + strip_h * 0.16 - ab[1]),
           author, font=author_font, fill=author_color)

rotated = strip.rotate(90, expand=True)
paste_x = (SPINE_W - rotated.width) // 2
paste_y = (FULL_H - rotated.height) // 2
spine.paste(rotated, (paste_x, paste_y), rotated)

canvas.paste(spine, (spine_x0, 0))

canvas.save(out_path, "PDF", resolution=DPI)
print(f"wrote {out_path}")
