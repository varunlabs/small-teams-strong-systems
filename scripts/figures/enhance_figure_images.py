#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

ROOT = Path(__file__).resolve().parents[2]
FIG_DIR = ROOT / "manuscript" / "figures" / "generated"


def enhance_one(path: Path):
    img = Image.open(path).convert("RGB")

    img = ImageEnhance.Contrast(img).enhance(1.08)
    img = ImageEnhance.Sharpness(img).enhance(1.15)
    img = ImageEnhance.Color(img).enhance(1.05)

    border = 24
    canvas = Image.new("RGB", (img.width + border * 2, img.height + border * 2), "#ffffff")
    canvas.paste(img, (border, border))

    draw = ImageDraw.Draw(canvas)
    draw.rectangle([0, 0, canvas.width - 1, canvas.height - 1], outline="#d9e2ef", width=3)

    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.rectangle([10, 10, canvas.width - 4, canvas.height - 4], fill=(20, 40, 70, 28))
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))

    out = Image.new("RGBA", canvas.size, (255, 255, 255, 255))
    out.alpha_composite(shadow)
    out.alpha_composite(canvas.convert("RGBA"))

    out.convert("RGB").save(path, format="PNG", optimize=True)


def main():
    files = sorted(FIG_DIR.glob("*.png"))
    if not files:
        print("No generated figures found.")
        return

    for file in files:
        enhance_one(file)
    print(f"Enhanced {len(files)} figure images in {FIG_DIR}")


if __name__ == "__main__":
    main()
