#!/usr/bin/env python3
"""Move Calibre's auto-generated Table of Contents from the end of the PDF to
its proper position (right after "Who This Book Is For", before the
Introduction), and correct every page number that move invalidates.

Calibre's --pdf-add-toc always appends the TOC at the end of the document and
bakes every page number as static text at generation time: both the running
footer on each page and the page numbers listed in the TOC itself. Moving the
TOC block earlier shifts everything from the insertion point onward by the
TOC's own page count, so those baked-in numbers go stale. This script:
  1. Locates the TOC block and the Introduction heading automatically (no
     hardcoded page indices, so it keeps working if the book's front matter
     or figure count changes).
  2. Reorders pages so the TOC sits before the Introduction.
  3. Re-stamps every footer number to match its new physical position.
  4. Re-stamps every TOC entry's listed number by the same page offset.

Usage: reposition-toc.py <input.pdf> <output.pdf> <gelasio-regular.ttf>
"""
import sys
import fitz
from pypdf import PdfReader, PdfWriter

src, dst, font_path = sys.argv[1:4]

fd = fitz.open(src)
n = len(fd)

# 1. Find the TOC block. Calibre's page-number footer extracts as the first
# text token on a Calibre-rendered page, so "Contents" is typically the
# second extracted line rather than the first.
toc_start = None
for i in range(n):
    lines = [l.strip() for l in fd[i].get_text().split("\n") if l.strip()]
    if "Contents" in lines[:2] and len(lines) > 5:
        toc_start = i
        break
if toc_start is None:
    raise SystemExit("reposition-toc: could not locate the TOC block (no 'Contents' page found)")

toc_end = toc_start
for i in range(toc_start, n - 1):  # never let the TOC swallow the back cover
    txt = fd[i].get_text()
    lines = [l for l in txt.split("\n") if l.strip()]
    digit_ratio = sum(1 for l in lines if l.strip()[-1:].isdigit()) / max(len(lines), 1)
    if digit_ratio > 0.3 and not fd[i].get_images():
        toc_end = i
    else:
        break
shift = toc_end - toc_start + 1

# 2. Find the Introduction heading (search only before the TOC, since the TOC
# itself also contains the word "Introduction" as a listed entry).
intro_page = None
for i in range(toc_start):
    head = " ".join(l.strip() for l in fd[i].get_text().split("\n")[:4]).upper()
    if "INTRODUCTION" in head and "REQUIRES" in head:
        intro_page = i
        break
if intro_page is None:
    raise SystemExit("reposition-toc: could not locate the Introduction heading")

threshold = intro_page  # footer number == fitz index in Calibre's original (unshifted) output
print(f"reposition-toc: TOC pages {toc_start}-{toc_end} ({shift} pages); "
      f"Introduction at page {intro_page}")
fd.close()

# 3. Reorder: front matter, then TOC, then the rest.
reader = PdfReader(src)
writer = PdfWriter()
order = (list(range(0, intro_page)) + list(range(toc_start, toc_end + 1)) +
         list(range(intro_page, toc_start)) + list(range(toc_end + 1, n)))
assert sorted(order) == list(range(n)), "reposition-toc: page set mismatch after reorder"
for idx in order:
    writer.add_page(reader.pages[idx])
reordered_path = dst + ".reordered.tmp.pdf"
with open(reordered_path, "wb") as f:
    writer.write(f)

# 4. Re-stamp footers (every content page = its own new sequential position)
# and TOC entry numbers (shift by `shift` for any entry pointing past the
# insertion point; entries before it are already correct).
font = fitz.Font(fontfile=font_path)
FONT_ALIAS = "gelasio-body"
d = fitz.open(reordered_path)
n2 = len(d)
new_toc_start, new_toc_end = intro_page, intro_page + shift - 1

for i in range(1, n2 - 1):  # skip front cover (0) and back cover (last)
    page = d[i]
    h = page.rect.height
    page.insert_font(fontname=FONT_ALIAS, fontfile=font_path)

    footer_span = None
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l.get("spans", []):
                if s["bbox"][3] > h * 0.85 and s["text"].strip().isdigit():
                    if footer_span is None or s["bbox"][3] > footer_span["bbox"][3]:
                        footer_span = s
    if footer_span:
        correct = i
        if footer_span["text"].strip() != str(correct):
            bbox = footer_span["bbox"]
            cx = (bbox[0] + bbox[2]) / 2
            size = footer_span["size"]
            page.add_redact_annot(fitz.Rect(bbox), fill=(1, 1, 1))
            page.apply_redactions()
            new_text = str(correct)
            tw = font.text_length(new_text, fontsize=size)
            page.insert_text((cx - tw / 2, bbox[3] - 2), new_text,
                              fontsize=size, fontname=FONT_ALIAS, fontfile=font_path)

    if new_toc_start <= i <= new_toc_end:
        w = page.rect.width
        spans_to_fix = []
        for b in page.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                spans = l.get("spans", [])
                if not spans:
                    continue
                last = spans[-1]
                txt = last["text"].strip()
                is_footer = footer_span is not None and last["bbox"] == footer_span["bbox"]
                if txt.isdigit() and not is_footer and last["bbox"][0] > w * 0.75:
                    spans_to_fix.append(last)
        for s in spans_to_fix:
            old_val = int(s["text"].strip())
            new_val = old_val + shift if old_val >= threshold else old_val
            if new_val == old_val:
                continue
            bbox = s["bbox"]
            right_edge = bbox[2]
            size = s["size"]
            page.add_redact_annot(fitz.Rect(bbox), fill=(1, 1, 1))
            page.apply_redactions()
            new_text = str(new_val)
            tw = font.text_length(new_text, fontsize=size)
            page.insert_text((right_edge - tw, bbox[3] - 2), new_text,
                              fontsize=size, fontname=FONT_ALIAS, fontfile=font_path)

d.save(dst)
d.close()
print(f"reposition-toc: wrote {dst} ({n2} pages)")
