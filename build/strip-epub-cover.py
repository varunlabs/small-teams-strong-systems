#!/usr/bin/env python3
"""Write a copy of an EPUB with its embedded cover removed.

The v2 EPUB embeds a cover (cover.xhtml in the spine + cover-image metadata).
For the PDF build we render the CONTENT only via Calibre and then wrap it with
the front/back cover pages ourselves (identical handling to v1). Removing the
embedded cover first prevents a doubled front cover. The committed EPUB is not
touched — this only produces a temporary cover-less copy.

Usage: strip-epub-cover.py <input.epub> <output.epub>
"""
import sys, re, zipfile

src, dst = sys.argv[1], sys.argv[2]
zin = zipfile.ZipFile(src, "r")
names = zin.namelist()
opf_name = next(n for n in names if n.endswith(".opf"))
opf = zin.read(opf_name).decode("utf-8")

# Remove cover metadata / spine reference / cover-image marker.
opf = re.sub(r'<meta[^>]*name="cover"[^>]*/>', "", opf)
opf = re.sub(r'<itemref[^>]*idref="cover_xhtml"[^>]*/>', "", opf)
opf = re.sub(r'<reference[^>]*type="cover"[^>]*/>', "", opf)
opf = re.sub(r'\s*properties="cover-image"', "", opf)

with zipfile.ZipFile(dst, "w") as zout:
    # mimetype must be first and stored uncompressed
    zout.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
    for n in names:
        if n == "mimetype":
            continue
        if n.endswith("cover.xhtml"):   # drop the cover page itself
            continue
        data = opf.encode("utf-8") if n == opf_name else zin.read(n)
        zout.writestr(n, data, compress_type=zipfile.ZIP_DEFLATED)
zin.close()
print(f"strip-epub-cover: wrote cover-less EPUB to {dst}")
