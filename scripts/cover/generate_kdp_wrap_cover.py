#!/usr/bin/env python3
from pathlib import Path
import json
import argparse
from PIL import Image, ImageOps, ImageDraw, ImageFont

try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None

ROOT = Path(__file__).resolve().parents[2]
COVER_DIR = ROOT / "manuscript" / "cover"
OUT_DIR = ROOT / "output" / "cover"
OUT_DIR.mkdir(parents=True, exist_ok=True)
INTERIOR_PDF = ROOT / "output" / "SmallTeamsStrongSystems_interior.pdf"
FALLBACK_PDF = ROOT / "output" / "SmallTeamsStrongSystems.pdf"

FRONT_PATH = COVER_DIR / "cover_front.png"
BACK_PATH = COVER_DIR / "cover_back.png"

TRIM_W_IN = 5.83   # A5 KDP trim width
TRIM_H_IN = 8.27   # A5 KDP trim height
BLEED_IN = 0.125
DPI = 300
DEFAULT_PAGE_COUNT = 344
BOOK_TITLE = "SMALL TEAMS, STRONG SYSTEMS"
BOOK_AUTHOR = "VARUN KUMAR SIDDARAJU"

# KDP spine factors by paper type
SPINE_PER_PAGE = {
    "white": 0.002252,
    "cream": 0.0025,
}


def to_px(inches: float) -> int:
    return int(round(inches * DPI))


def get_font(size: int):
    for path in [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def detect_page_count() -> int:
    if PdfReader is None:
        return DEFAULT_PAGE_COUNT

    pdf_path = INTERIOR_PDF if INTERIOR_PDF.exists() else FALLBACK_PDF
    if not pdf_path.exists():
        return DEFAULT_PAGE_COUNT
    try:
        return len(PdfReader(str(pdf_path)).pages)
    except Exception:
        return DEFAULT_PAGE_COUNT


def add_spine_text(wrap: Image.Image, spine_x: int, spine_px: int, total_h_px: int):
    if spine_px < 48:
        return

    text = f"{BOOK_TITLE}  •  {BOOK_AUTHOR}"
    font = get_font(max(18, min(42, spine_px // 3)))

    text_img = Image.new("RGBA", (total_h_px, spine_px), (0, 0, 0, 0))
    d = ImageDraw.Draw(text_img)
    bbox = d.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = max(8, (text_img.width - tw) // 2)
    ty = max(4, (text_img.height - th) // 2)
    d.text((tx, ty), text, fill=(235, 242, 255, 255), font=font)

    rotated = text_img.rotate(90, expand=True)
    rx = spine_x + max(0, (spine_px - rotated.width) // 2)
    ry = max(0, (total_h_px - rotated.height) // 2)
    wrap.paste(rotated.convert("RGB"), (rx, ry), rotated)


def build_wrap(paper_type: str, spine_factor: float, page_count: int, include_spine_text: bool):
    spine_in = page_count * spine_factor
    total_w_in = (2 * TRIM_W_IN) + spine_in + (2 * BLEED_IN)
    total_h_in = TRIM_H_IN + (2 * BLEED_IN)

    total_w_px = to_px(total_w_in)
    total_h_px = to_px(total_h_in)

    bleed_px = to_px(BLEED_IN)
    trim_w_px = to_px(TRIM_W_IN)
    trim_h_px = to_px(TRIM_H_IN)
    spine_px = to_px(spine_in)

    wrap = Image.new("RGB", (total_w_px, total_h_px), (255, 255, 255))

    front = Image.open(FRONT_PATH).convert("RGB")
    back = Image.open(BACK_PATH).convert("RGB")

    panel_w = trim_w_px + bleed_px
    panel_h = trim_h_px + (2 * bleed_px)

    back_panel = ImageOps.fit(back, (panel_w, panel_h), method=Image.Resampling.LANCZOS)
    front_panel = ImageOps.fit(front, (panel_w, panel_h), method=Image.Resampling.LANCZOS)

    wrap.paste(back_panel, (0, 0))

    spine_x = panel_w
    spine_h = panel_h
    if spine_px > 0:
        spine_strip = Image.new("RGB", (spine_px, spine_h), (28, 37, 66))
        wrap.paste(spine_strip, (spine_x, 0))
        if include_spine_text:
            add_spine_text(wrap, spine_x, spine_px, total_h_px)

    front_x = panel_w + spine_px
    wrap.paste(front_panel, (front_x, 0))

    out_png = OUT_DIR / f"kdp_wrap_a5_{paper_type}_{page_count}p_300dpi.png"
    wrap.save(out_png, format="PNG")

    proof = wrap.copy()
    guide = ImageDraw.Draw(proof)
    guide_color = (180, 180, 180)

    guide.line([(bleed_px, 0), (bleed_px, total_h_px)], fill=guide_color, width=1)
    guide.line([(total_w_px - bleed_px, 0), (total_w_px - bleed_px, total_h_px)], fill=guide_color, width=1)
    guide.line([(0, bleed_px), (total_w_px, bleed_px)], fill=guide_color, width=1)
    guide.line([(0, total_h_px - bleed_px), (total_w_px, total_h_px - bleed_px)], fill=guide_color, width=1)
    guide.line([(spine_x, 0), (spine_x, total_h_px)], fill=guide_color, width=1)
    guide.line([(spine_x + spine_px, 0), (spine_x + spine_px, total_h_px)], fill=guide_color, width=1)

    out_proof = OUT_DIR / f"kdp_wrap_a5_{paper_type}_{page_count}p_300dpi_proof.png"
    proof.save(out_proof, format="PNG")

    out_pdf = OUT_DIR / f"kdp_wrap_a5_{paper_type}_{page_count}p_300dpi_flattened.pdf"
    wrap.save(out_pdf, "PDF", resolution=DPI)

    specs = {
        "paper_type": paper_type,
        "page_count": page_count,
        "trim_size_inches": {"width": TRIM_W_IN, "height": TRIM_H_IN},
        "bleed_inches": BLEED_IN,
        "spine_width_inches": round(spine_in, 6),
        "total_cover_inches": {"width": round(total_w_in, 6), "height": round(total_h_in, 6)},
        "dpi": DPI,
        "total_cover_pixels": {"width": total_w_px, "height": total_h_px},
        "source_front": str(FRONT_PATH.relative_to(ROOT)),
        "source_back": str(BACK_PATH.relative_to(ROOT)),
        "output_wrap": str(out_png.relative_to(ROOT)),
        "output_flattened_pdf": str(out_pdf.relative_to(ROOT)),
    }

    out_json = OUT_DIR / f"kdp_wrap_a5_{paper_type}_{page_count}p_specs.json"
    out_json.write_text(json.dumps(specs, indent=2), encoding="utf-8")

    return out_png, out_proof, out_pdf, out_json


def main():
    parser = argparse.ArgumentParser(description="Generate KDP full-wrap cover files.")
    parser.add_argument("--paper-type", choices=["white", "cream", "both"], default="both")
    parser.add_argument("--no-spine-text", action="store_true")
    args = parser.parse_args()

    if not FRONT_PATH.exists() or not BACK_PATH.exists():
        raise FileNotFoundError("Missing cover_front.png or cover_back.png in manuscript/cover")

    page_count = detect_page_count()
    outputs = []
    for paper_type, factor in SPINE_PER_PAGE.items():
        if args.paper_type != "both" and paper_type != args.paper_type:
            continue
        outputs.append(build_wrap(paper_type, factor, page_count, include_spine_text=not args.no_spine_text))

    for png, proof, pdf, spec in outputs:
        print(png)
        print(proof)
        print(pdf)
        print(spec)


if __name__ == "__main__":
    main()
