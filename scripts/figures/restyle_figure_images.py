#!/usr/bin/env python3
"""Restyle generated figure PNGs into a consistent illustration look.

This script:
- Backs up existing files from manuscript/figures/generated -> manuscript/figures/generated_original
- Overwrites the original filenames in manuscript/figures/generated

Rationale: chapter Markdown references are already wired to manuscript/figures/generated/*.png.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parents[2]
FIG_DIR = ROOT / "manuscript" / "figures" / "generated"
BACKUP_DIR = ROOT / "manuscript" / "figures" / "generated_original"


@dataclass(frozen=True)
class Style:
    ink: tuple[int, int, int] = (15, 23, 45)  # deep navy
    paper: tuple[int, int, int] = (255, 255, 255)
    wash_dark: tuple[int, int, int] = (217, 226, 239)  # very light blue-gray
    frame: tuple[int, int, int] = (217, 226, 239)
    edge_cutoff: int = 40
    edge_contrast: float = 2.2
    blur_radius: float = 2.2
    final_contrast: float = 1.08
    final_sharpness: float = 1.15


STYLE_PRESETS: dict[str, Style] = {
    # Balanced default for this manuscript's technical/editorial tone.
    "executive_navy": Style(
        ink=(15, 23, 45),
        paper=(255, 255, 255),
        wash_dark=(217, 226, 239),
        frame=(217, 226, 239),
        edge_cutoff=40,
        edge_contrast=2.2,
        blur_radius=2.2,
        final_contrast=1.08,
        final_sharpness=1.15,
    ),
    # Cooler and more technical, useful when figures are dense.
    "blueprint": Style(
        ink=(10, 33, 66),
        paper=(252, 254, 255),
        wash_dark=(208, 221, 238),
        frame=(198, 214, 234),
        edge_cutoff=42,
        edge_contrast=2.35,
        blur_radius=2.0,
        final_contrast=1.1,
        final_sharpness=1.18,
    ),
    # Warmer editorial look that feels less "slide deck".
    "warm_editorial": Style(
        ink=(44, 34, 25),
        paper=(255, 253, 248),
        wash_dark=(239, 231, 219),
        frame=(231, 222, 210),
        edge_cutoff=39,
        edge_contrast=2.05,
        blur_radius=2.35,
        final_contrast=1.06,
        final_sharpness=1.12,
    ),
    # Maximum print robustness for grayscale and low-quality displays.
    "mono_print": Style(
        ink=(20, 20, 20),
        paper=(255, 255, 255),
        wash_dark=(226, 226, 226),
        frame=(208, 208, 208),
        edge_cutoff=45,
        edge_contrast=2.45,
        blur_radius=1.9,
        final_contrast=1.16,
        final_sharpness=1.2,
    ),
    # Sparse line-art treatment with minimal background wash.
    "minimal_lineart": Style(
        ink=(18, 29, 48),
        paper=(255, 255, 255),
        wash_dark=(244, 247, 251),
        frame=(228, 234, 242),
        edge_cutoff=48,
        edge_contrast=2.55,
        blur_radius=1.7,
        final_contrast=1.14,
        final_sharpness=1.24,
    ),
    # Soft pastel look with gentler contrast transitions.
    "pastel_soft": Style(
        ink=(55, 70, 96),
        paper=(253, 253, 255),
        wash_dark=(232, 239, 249),
        frame=(219, 229, 241),
        edge_cutoff=36,
        edge_contrast=1.95,
        blur_radius=2.55,
        final_contrast=1.03,
        final_sharpness=1.08,
    ),
    # Bold poster-style contrast for slide-like impact.
    "high_contrast_poster": Style(
        ink=(8, 16, 30),
        paper=(255, 255, 255),
        wash_dark=(206, 220, 236),
        frame=(189, 206, 226),
        edge_cutoff=50,
        edge_contrast=2.8,
        blur_radius=1.6,
        final_contrast=1.2,
        final_sharpness=1.28,
    ),
    # Dark-theme inverse look suitable for presentations.
    "dark_inverse": Style(
        ink=(232, 240, 255),
        paper=(22, 28, 39),
        wash_dark=(42, 52, 70),
        frame=(60, 73, 95),
        edge_cutoff=38,
        edge_contrast=2.15,
        blur_radius=2.1,
        final_contrast=1.1,
        final_sharpness=1.16,
    ),
    # Warm earthy print style with editorial character.
    "earth_tone": Style(
        ink=(58, 45, 33),
        paper=(252, 248, 239),
        wash_dark=(232, 220, 201),
        frame=(220, 206, 184),
        edge_cutoff=40,
        edge_contrast=2.1,
        blur_radius=2.25,
        final_contrast=1.07,
        final_sharpness=1.12,
    ),
    # Cyanotype-inspired technical aesthetic.
    "cyanotype": Style(
        ink=(12, 49, 92),
        paper=(246, 251, 255),
        wash_dark=(200, 222, 244),
        frame=(182, 208, 235),
        edge_cutoff=43,
        edge_contrast=2.35,
        blur_radius=2.0,
        final_contrast=1.11,
        final_sharpness=1.18,
    ),
}


def _threshold(img_l: Image.Image, cutoff: int) -> Image.Image:
    return img_l.point(lambda p: 255 if p >= cutoff else 0)


def restyle_image(img: Image.Image, style: Style) -> Image.Image:
    # Work in RGB throughout (keep text crisp).
    rgb = img.convert("RGB")

    gray = ImageOps.grayscale(rgb)
    gray = ImageOps.autocontrast(gray)
    gray = gray.filter(ImageFilter.MedianFilter(size=3))

    # Build an "ink" layer using edges + thresholding.
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edges = ImageOps.autocontrast(edges)
    edges = ImageEnhance.Contrast(edges).enhance(style.edge_contrast)

    # Threshold and thicken a bit.
    ink_mask = _threshold(edges, cutoff=style.edge_cutoff)
    ink_mask = ImageOps.invert(ink_mask)  # black where ink should be
    ink_mask = ink_mask.filter(ImageFilter.MaxFilter(size=3))

    # Create a light "wash" background from a low-frequency version of the image.
    wash = gray.filter(ImageFilter.GaussianBlur(radius=style.blur_radius))
    wash = ImageOps.autocontrast(wash)

    # Posterize softly to get a flatter illustration vibe while keeping labels readable.
    wash_rgb = ImageOps.colorize(wash, black=style.wash_dark, white=style.paper)

    # Colorize ink and composite.
    ink_rgb = ImageOps.colorize(ink_mask, black=style.ink, white=style.paper)
    out = ImageChops.multiply(wash_rgb, ink_rgb)

    # Final tuning.
    out = ImageEnhance.Contrast(out).enhance(style.final_contrast)
    out = ImageEnhance.Sharpness(out).enhance(style.final_sharpness)

    # Add a clean border consistent with the rest of the book assets.
    border = max(18, int(min(out.size) * 0.012))
    canvas = Image.new("RGB", (out.width + border * 2, out.height + border * 2), style.paper)
    canvas.paste(out, (border, border))

    # Subtle frame.
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([0, 0, canvas.width - 1, canvas.height - 1], outline=style.frame, width=3)

    return canvas


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Restyle generated figure PNGs with selectable visual presets.")
    parser.add_argument(
        "--style",
        default="executive_navy",
        choices=sorted(STYLE_PRESETS.keys()),
        help="Preset style name.",
    )
    parser.add_argument(
        "--source",
        choices=["generated", "generated_original"],
        default="generated",
        help="Which directory to read from before writing to generated.",
    )
    parser.add_argument(
        "--list-styles",
        action="store_true",
        help="Print available style names and exit.",
    )
    return parser.parse_args()


def _source_dir(source: str) -> Path:
    if source == "generated_original":
        return BACKUP_DIR
    return FIG_DIR


def main() -> int:
    args = _parse_args()

    if args.list_styles:
        for name in sorted(STYLE_PRESETS):
            print(name)
        return 0

    source_dir = _source_dir(args.source)
    if not source_dir.exists():
        raise SystemExit(f"Missing source directory: {source_dir}")

    if not FIG_DIR.exists():
        raise SystemExit(f"Missing figures directory: {FIG_DIR}")

    files = sorted(source_dir.glob("*.png"))
    if not files:
        print(f"No PNG figures found in {source_dir}")
        return 0

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    style = STYLE_PRESETS[args.style]
    processed = 0
    for path in files:
        out_path = FIG_DIR / path.name

        backup = BACKUP_DIR / out_path.name
        if not backup.exists() and out_path.exists():
            backup.write_bytes(out_path.read_bytes())

        img = Image.open(path)
        out = restyle_image(img, style)
        out.save(out_path, format="PNG", optimize=True)
        processed += 1

    print(
        f"Restyled {processed} figures using '{args.style}' from {source_dir.name} -> {FIG_DIR.name} "
        f"(backups in {BACKUP_DIR})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
