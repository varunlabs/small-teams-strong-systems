#!/usr/bin/env python3
"""Audit manuscript figure references.

Reports:
- Missing local image targets referenced from Markdown
- Figure numbering gaps / duplicates per chapter file

This is intentionally conservative: it only checks explicit "Figure X.Y —" headings
and Markdown image links.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT_DIR = ROOT / "manuscript"

# Markdown image: ![alt](path "title")
IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")

# Figure heading line format used in this repo: > **Figure 2.1 — Title**
# Match both em dash and hyphen just in case.
FIG_HEADING_RE = re.compile(r"\*\*Figure\s+(\d+)\.(\d+)\s+[—-]\s+(.+?)\*\*")


@dataclass(frozen=True)
class MissingImage:
    markdown_file: Path
    target: str


@dataclass(frozen=True)
class FigureHeading:
    markdown_file: Path
    major: int
    minor: int
    line: int


def iter_markdown_files() -> list[Path]:
    return sorted(MANUSCRIPT_DIR.glob("**/*.md"))


def parse_markdown(md_path: Path) -> tuple[list[MissingImage], list[FigureHeading]]:
    text = md_path.read_text(encoding="utf-8")

    missing: list[MissingImage] = []
    headings: list[FigureHeading] = []

    # Images
    for match in IMG_RE.finditer(text):
        raw_target = match.group(1).strip()
        # Drop optional title string if present
        target = raw_target.split()[0]
        if target.startswith(("http://", "https://", "data:")):
            continue
        # In this repo, many figure links are written as repo-root-relative
        # paths like "manuscript/figures/..." so they work consistently when
        # pandoc is run from the repo root.
        if target.startswith("manuscript/"):
            resolved = (ROOT / target).resolve()
        else:
            resolved = (md_path.parent / target).resolve()
        if not resolved.exists():
            missing.append(MissingImage(md_path, target))

    # Figure headings
    for line_no, line in enumerate(text.splitlines(), 1):
        match = FIG_HEADING_RE.search(line)
        if match:
            headings.append(
                FigureHeading(
                    markdown_file=md_path,
                    major=int(match.group(1)),
                    minor=int(match.group(2)),
                    line=line_no,
                )
            )

    return missing, headings


def main() -> int:
    if not MANUSCRIPT_DIR.exists():
        raise SystemExit(f"Missing directory: {MANUSCRIPT_DIR}")

    all_missing: list[MissingImage] = []
    all_headings: list[FigureHeading] = []

    md_files = iter_markdown_files()
    for md in md_files:
        missing, headings = parse_markdown(md)
        all_missing.extend(missing)
        all_headings.extend(headings)

    print(f"Markdown files: {len(md_files)}")
    print(f"Figure headings: {len(all_headings)}")

    print(f"\nMissing image targets: {len(all_missing)}")
    for item in all_missing[:100]:
        rel = item.markdown_file.relative_to(ROOT)
        print(f" - {rel} -> {item.target}")
    if len(all_missing) > 100:
        print(" - ...")

    # Issues per file, per major
    print("\nFigure numbering issues:")
    issues = 0
    by_file: dict[Path, list[FigureHeading]] = {}
    for heading in all_headings:
        by_file.setdefault(heading.markdown_file, []).append(heading)

    for md_path in sorted(by_file):
        figs = by_file[md_path]
        # Only compare minors within the same major number.
        by_major: dict[int, list[FigureHeading]] = {}
        for f in figs:
            by_major.setdefault(f.major, []).append(f)

        for major, items in sorted(by_major.items()):
            minors = [f.minor for f in items]
            seen: set[int] = set()
            dupes: list[int] = []
            for m in minors:
                if m in seen:
                    dupes.append(m)
                else:
                    seen.add(m)
            dupes = sorted(set(dupes))

            minor_set = set(minors)
            max_minor = max(minors)
            gaps = [n for n in range(1, max_minor + 1) if n not in minor_set]

            if dupes or gaps:
                rel = md_path.relative_to(ROOT)
                issues += 1
                parts = []
                if dupes:
                    parts.append(f"dupes={dupes}")
                if gaps:
                    parts.append(f"gaps={gaps}")
                print(f" - {rel} (Figure {major}.x): " + ", ".join(parts))

    if issues == 0:
        print(" - none")

    return 1 if all_missing or issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
