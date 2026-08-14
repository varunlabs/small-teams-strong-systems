#!/usr/bin/env python3
"""Drop truly-blank interior pages from a PDF.

A page counts as blank when it carries no real embedded image and no text
beyond its own page number. Calibre renders the page-number footer as a
reusable Form XObject (not an Image XObject) on every single page, so a naive
"/XObject in resources" check is always true and never flags anything as
blank -- only /Subtype == /Image XObjects count as "this page has real
content". The book has no intentional blank pages, so removing them is safe.

Usage: strip-blank-pages.py <input.pdf> <output.pdf>
"""
import sys
from pypdf import PdfReader, PdfWriter
from pypdf.generic import IndirectObject

src, dst = sys.argv[1], sys.argv[2]
reader = PdfReader(src)
writer = PdfWriter()
dropped = 0
for page in reader.pages:
    text = (page.extract_text() or "").strip()
    resources = page.get("/Resources") or {}
    xobjects = resources.get("/XObject") or {}
    has_real_image = False
    for xobj in xobjects.values():
        obj = xobj.get_object() if isinstance(xobj, IndirectObject) else xobj
        if obj.get("/Subtype") == "/Image":
            has_real_image = True
            break
    if len(text) < 5 and not has_real_image:
        dropped += 1
        continue
    writer.add_page(page)

with open(dst, "wb") as fh:
    writer.write(fh)

print(f"strip-blank-pages: dropped {dropped} blank interior page(s)")
