#!/usr/bin/env python3
import os
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT = ROOT / "manuscript"
OUT_DIR = MANUSCRIPT / "figures" / "generated"

FIG_RE = re.compile(r"^\s*>\s*\*\*Figure\s+([0-9]+\.[0-9]+)\s+—\s+(.+?)\*\*\s*$")
TABLE_LINE_RE = re.compile(r"^\s*>\s*\|.*\|\s*$")


def parse_row(md_line: str):
    line = re.sub(r"^\s*>\s*", "", md_line).strip()
    if not line.startswith("|"):
        return None
    parts = [cell.strip() for cell in line.strip("|").split("|")]
    return parts


def is_separator_row(cells):
    if not cells:
        return False
    return all(re.fullmatch(r":?-{3,}:?", c.replace(" ", "")) is not None for c in cells)


def clean_text(text: str):
    return re.sub(r"\s+", " ", text).strip()


def measure_text(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_table_png(headers, rows, title, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)

    font = ImageFont.load_default()
    title_font = ImageFont.load_default()

    columns = max(len(headers), max((len(r) for r in rows), default=0))
    headers = headers + [""] * (columns - len(headers))
    rows = [r + [""] * (columns - len(r)) for r in rows]

    pad_x = 20
    pad_y = 12
    row_h = 48
    title_h = 84

    tmp = Image.new("RGB", (10, 10), "white")
    draw = ImageDraw.Draw(tmp)

    col_widths = []
    for col in range(columns):
        max_w = measure_text(draw, headers[col], font)[0]
        for row in rows:
            max_w = max(max_w, measure_text(draw, row[col], font)[0])
        col_widths.append(max(220, min(520, max_w + pad_x * 2)))

    table_w = sum(col_widths)
    table_h = row_h * (1 + len(rows))

    left = 40
    top = 40
    width = left * 2 + table_w
    height = top * 2 + title_h + table_h

    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, width - 1, height - 1], fill="#f8fbff")
    draw.rectangle([0, 0, width - 1, height - 1], outline="#d3dce8", width=2)

    draw.rounded_rectangle([left, top, width - left, top + title_h - 16], radius=18, fill="#1f3a63")
    draw.text((left + 16, top + 24), clean_text(title), fill="#f5f9ff", font=title_font)

    y = top + title_h
    x = left
    for i, w in enumerate(col_widths):
        draw.rectangle([x, y, x + w, y + row_h], fill="#dfe9f8", outline="#b5c6de", width=1)
        draw.text((x + pad_x, y + pad_y), clean_text(headers[i]), fill="#12253f", font=font)
        x += w

    for r_idx, row in enumerate(rows):
        y_row = y + row_h * (r_idx + 1)
        x = left
        fill = "#ffffff" if r_idx % 2 == 0 else "#f5f8fc"
        for c_idx, w in enumerate(col_widths):
            draw.rectangle([x, y_row, x + w, y_row + row_h], fill=fill, outline="#dbe4ef", width=1)
            draw.text((x + pad_x, y_row + pad_y), clean_text(row[c_idx]), fill="#202938", font=font)
            x += w

    img.save(out_path)


def convert_file(md_path: Path):
    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=False)

    changed = False
    out_lines = []

    current_figure_num = None
    current_figure_title = None

    i = 0
    while i < len(lines):
        line = lines[i]

        fig = FIG_RE.match(line)
        if fig:
            current_figure_num = fig.group(1)
            current_figure_title = fig.group(2)
            out_lines.append(line)
            i += 1
            continue

        if current_figure_num and TABLE_LINE_RE.match(line):
            table_lines = []
            while i < len(lines) and TABLE_LINE_RE.match(lines[i]):
                table_lines.append(lines[i])
                i += 1

            parsed = [parse_row(l) for l in table_lines]
            parsed = [p for p in parsed if p]
            if len(parsed) >= 2 and is_separator_row(parsed[1]):
                headers = parsed[0]
                rows = parsed[2:]

                safe_stem = re.sub(r"[^a-zA-Z0-9_]+", "_", md_path.stem).strip("_").lower()
                fig_id = current_figure_num.replace(".", "_")
                img_name = f"{safe_stem}_fig_{fig_id}.png"
                img_path = OUT_DIR / img_name

                full_title = f"Figure {current_figure_num} — {current_figure_title}"
                draw_table_png(headers, rows, full_title, img_path)

                rel = os.path.relpath(img_path, md_path.parent).replace(os.sep, "/")
                out_lines.append(">")
                out_lines.append(f"> ![{full_title}]({rel})")
                out_lines.append(">")
                changed = True
            else:
                out_lines.extend(table_lines)
            continue

        if line.strip() == "---":
            current_figure_num = None
            current_figure_title = None

        out_lines.append(line)
        i += 1

    if changed:
        md_path.write_text("\n".join(out_lines) + "\n", encoding="utf-8")

    return changed


def main():
    md_files = sorted(MANUSCRIPT.glob("**/*.md"))
    changed_count = 0
    for path in md_files:
        if convert_file(path):
            changed_count += 1
    print(f"Updated markdown files: {changed_count}")
    print(f"Generated image directory: {OUT_DIR}")


if __name__ == "__main__":
    main()
