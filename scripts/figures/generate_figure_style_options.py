#!/usr/bin/env python3
"""Generate side-by-side sample outputs for figure style selection.

Produces:
- output/figure_style_options/<style>/<original_filename>.png
- output/figure_style_options/contact_sheet_<style>.png

This lets you compare visual directions before regenerating all figures.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from restyle_figure_images import STYLE_PRESETS, FIG_DIR, BACKUP_DIR, restyle_image


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "output" / "figure_style_options"


DEFAULT_SAMPLE_FILES = [
    "ch01_why_big_teams_fig_1_1.png",
    "ch02_end_of_linear_scaling_fig_2_1.png",
    "ch06_six_core_roles_fig_6_1.png",
    "ch08_designing_speed_fig_8_1.png",
    "ch13_leadership_fig_13_1.png",
]


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
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def choose_source_dir() -> Path:
    if BACKUP_DIR.exists() and any(BACKUP_DIR.glob("*.png")):
        return BACKUP_DIR
    return FIG_DIR


def _resolve_sample_files(source_dir: Path, requested: list[str] | None) -> list[Path]:
    if requested:
        chosen = [source_dir / name for name in requested]
    else:
        chosen = [source_dir / name for name in DEFAULT_SAMPLE_FILES]

    existing = [p for p in chosen if p.exists()]
    if existing:
        return existing

    fallback = sorted(source_dir.glob("*.png"))[:5]
    if fallback:
        return fallback
    return []


def _make_contact_sheet(style_name: str, files: list[Path], style_dir: Path):
    if not files:
        return

    tile_w = 760
    tile_h = 360
    cols = 2
    rows = (len(files) + cols - 1) // cols

    margin = 32
    header_h = 100
    gutter = 24

    sheet_w = margin * 2 + cols * tile_w + (cols - 1) * gutter
    sheet_h = margin * 2 + header_h + rows * tile_h + (rows - 1) * gutter

    sheet = Image.new("RGB", (sheet_w, sheet_h), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)

    title_font = get_font(40, bold=True)
    label_font = get_font(20)

    draw.text((margin, margin), f"Figure Style Preview: {style_name}", font=title_font, fill=(20, 24, 33))

    start_y = margin + header_h
    for i, source in enumerate(files):
        r = i // cols
        c = i % cols
        x = margin + c * (tile_w + gutter)
        y = start_y + r * (tile_h + gutter)

        original = Image.open(source).convert("RGB")
        styled = Image.open(style_dir / source.name).convert("RGB")

        preview_h = tile_h - 64
        half_w = (tile_w - 42) // 2

        original.thumbnail((half_w, preview_h), Image.Resampling.LANCZOS)
        styled.thumbnail((half_w, preview_h), Image.Resampling.LANCZOS)

        cell = Image.new("RGB", (tile_w, tile_h), (248, 251, 255))
        oy = 24 + (preview_h - original.height) // 2
        sy = 24 + (preview_h - styled.height) // 2
        ox = 14 + (half_w - original.width) // 2
        sx = 28 + half_w + (half_w - styled.width) // 2

        cell.paste(original, (ox, oy))
        cell.paste(styled, (sx, sy))

        cell_draw = ImageDraw.Draw(cell)
        cell_draw.rectangle([0, 0, tile_w - 1, tile_h - 1], outline=(217, 226, 239), width=2)
        cell_draw.line([(tile_w // 2, 14), (tile_w // 2, tile_h - 40)], fill=(217, 226, 239), width=2)
        cell_draw.text((18, 8), "ORIGINAL", font=label_font, fill=(98, 108, 120))
        cell_draw.text((tile_w // 2 + 18, 8), "STYLED", font=label_font, fill=(98, 108, 120))
        cell_draw.text((14, tile_h - 30), source.stem, font=label_font, fill=(80, 88, 98))

        sheet.paste(cell, (x, y))

    sheet.save(OUT_DIR / f"contact_sheet_{style_name}.png", format="PNG", optimize=True)


def generate_for_style(style_name: str, samples: list[Path]):
    style = STYLE_PRESETS[style_name]
    style_dir = OUT_DIR / style_name
    style_dir.mkdir(parents=True, exist_ok=True)

    for sample_path in samples:
        src = Image.open(sample_path)
        out = restyle_image(src, style)
        out.save(style_dir / sample_path.name, format="PNG", optimize=True)

    _make_contact_sheet(style_name, samples, style_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate style option samples for figure regeneration.")
    parser.add_argument(
        "--styles",
        nargs="*",
        default=sorted(STYLE_PRESETS.keys()),
        help="Subset of style names to render.",
    )
    parser.add_argument(
        "--files",
        nargs="*",
        default=None,
        help="Optional list of source figure filenames.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    unknown = sorted(set(args.styles) - set(STYLE_PRESETS.keys()))
    if unknown:
        raise SystemExit(f"Unknown style(s): {', '.join(unknown)}")

    source_dir = choose_source_dir()
    samples = _resolve_sample_files(source_dir, args.files)
    if not samples:
        raise SystemExit(f"No sample PNGs found in {source_dir}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for style_name in args.styles:
        generate_for_style(style_name, samples)

    print(f"Generated style previews in {OUT_DIR}")
    print(f"Source figures: {source_dir}")
    print("Styles:", ", ".join(args.styles))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
