#!/usr/bin/env python3
"""Drop truly-blank interior pages from a PDF.

Used for the v1 PDF: the book class leaves an empty verso between the table of
contents and the first content page. A page counts as blank when it carries no
image and no text beyond its own page number. The book has no intentional blank
pages, so removing them is safe and makes v1 match v2 (zero interior blanks).

Usage: strip-blank-pages.py <input.pdf> <output.pdf>
"""
import sys
from pypdf import PdfReader, PdfWriter

src, dst = sys.argv[1], sys.argv[2]
reader = PdfReader(src)
writer = PdfWriter()
dropped = 0
for page in reader.pages:
    text = (page.extract_text() or "").strip()
    resources = page.get("/Resources") or {}
    has_image = "/XObject" in resources
    if len(text) < 5 and not has_image:
        dropped += 1
        continue
    writer.add_page(page)

with open(dst, "wb") as fh:
    writer.write(fh)

print(f"strip-blank-pages: dropped {dropped} blank interior page(s)")
