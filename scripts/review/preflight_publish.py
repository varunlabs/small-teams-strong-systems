#!/usr/bin/env python3
"""Run end-to-end publication preflight checks.

This script runs the core quality gates and build steps in order:
1) Readability review
2) Figure audit
3) Editorial final review
4) EPUB + DOCX build
5) PDF build
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def run_step(label: str, command: list[str]) -> None:
    print(f"\n[{label}] {' '.join(command)}")
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> int:
    print("=" * 72)
    print("PUBLICATION PREFLIGHT")
    print("=" * 72)
    print(f"Working directory: {ROOT}")

    run_step("1/5 Readability", ["python3", "scripts/review/readability_review.py"])
    run_step("2/5 Figure Audit", ["python3", "scripts/review/audit_figures.py"])
    run_step("3/5 Editorial Review", ["python3", "scripts/review/final_review.py"])
    run_step("4/5 EPUB+DOCX Build", ["bash", "build.sh"])
    run_step("5/5 PDF Build", ["bash", "build_pdf.sh"])

    print("\n" + "=" * 72)
    print("PREFLIGHT PASS: All checks and builds completed successfully")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
