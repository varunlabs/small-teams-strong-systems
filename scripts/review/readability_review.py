#!/usr/bin/env python3
"""Readability review for manuscript chapters.

Metrics:
- Flesch Reading Ease (higher is easier)
- Flesch-Kincaid Grade Level
- Gunning Fog Index
- SMOG Index
- Automated Readability Index (ARI)

This script uses a lightweight in-house syllable estimator to avoid external
dependencies and keep CI/build environments simple.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT = ROOT / "manuscript"


CHAPTER_FILES = [
    "part1/ch01_why_big_teams.md",
    "part1/ch02_end_of_linear_scaling.md",
    "part1/ch03_what_ai_changes.md",
    "part2/ch04_headcount_to_leverage.md",
    "part2/ch05_why_six.md",
    "part2/ch06_six_core_roles.md",
    "part2/ch07_human_judgment.md",
    "part2/ch08_designing_speed.md",
    "part3/ch09_rapid_prototyping.md",
    "part3/ch10_decision_making.md",
    "part3/ch11_small_teams.md",
    "part3/ch12_ai_xr_frontier.md",
    "part4/ch13_leadership.md",
    "part4/ch14_burnout.md",
    "part4/ch15_when_to_hire.md",
    "part4/ch16_scaling.md",
]


WORD_RE = re.compile(r"[A-Za-z][A-Za-z'\-]*")
SENTENCE_RE = re.compile(r"[.!?]+")


@dataclass
class ChapterMetrics:
    chapter: str
    words: int
    sentences: int
    syllables: int
    complex_words: int
    characters: int
    flesch_reading_ease: float
    fk_grade: float
    gunning_fog: float
    smog: float
    ari: float


def strip_markdown(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s{0,3}>\s?", "", text, flags=re.MULTILINE)
    text = re.sub(r"[*_~]", "", text)
    return text


def estimate_syllables(word: str) -> int:
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 1
    if len(w) <= 3:
        return 1

    vowels = "aeiouy"
    groups = 0
    prev_vowel = False
    for char in w:
        is_vowel = char in vowels
        if is_vowel and not prev_vowel:
            groups += 1
        prev_vowel = is_vowel

    if w.endswith("e") and not w.endswith(("le", "ye")) and groups > 1:
        groups -= 1

    if w.endswith("ed") and len(w) > 3 and w[-3] not in vowels and groups > 1:
        groups -= 1

    return max(1, groups)


def compute_metrics(chapter_path: Path) -> ChapterMetrics:
    raw = chapter_path.read_text(encoding="utf-8")
    text = strip_markdown(raw)

    words = WORD_RE.findall(text)
    word_count = len(words)
    sentence_count = len(SENTENCE_RE.findall(text))
    if sentence_count == 0:
        sentence_count = 1

    syllable_count = sum(estimate_syllables(word) for word in words)
    character_count = sum(len(re.sub(r"[^A-Za-z0-9]", "", word)) for word in words)
    complex_word_count = sum(1 for word in words if estimate_syllables(word) >= 3)

    if word_count == 0:
        word_count = 1

    asl = word_count / sentence_count
    asw = syllable_count / word_count

    flesch = 206.835 - 1.015 * asl - 84.6 * asw
    fk_grade = 0.39 * asl + 11.8 * asw - 15.59
    gunning_fog = 0.4 * (asl + 100 * (complex_word_count / word_count))
    smog = 1.043 * math.sqrt(complex_word_count * (30 / sentence_count)) + 3.1291
    ari = 4.71 * (character_count / word_count) + 0.5 * asl - 21.43

    return ChapterMetrics(
        chapter=chapter_path.name,
        words=word_count,
        sentences=sentence_count,
        syllables=syllable_count,
        complex_words=complex_word_count,
        characters=character_count,
        flesch_reading_ease=round(flesch, 2),
        fk_grade=round(fk_grade, 2),
        gunning_fog=round(gunning_fog, 2),
        smog=round(smog, 2),
        ari=round(ari, 2),
    )


def status(metric: float, low: float, high: float, reverse: bool = False) -> str:
    if reverse:
        return "PASS" if metric >= low else "WARN"
    return "PASS" if low <= metric <= high else "WARN"


def main() -> int:
    print("=" * 68)
    print("READABILITY REVIEW")
    print("=" * 68)
    print("Targets for professional/technical nonfiction:")
    print("  - Flesch Reading Ease: >= 17")
    print("  - Flesch-Kincaid Grade: 8 to 14")
    print("  - Gunning Fog: 10 to 17.5")
    print("  - SMOG: 10 to 15.5")
    print("  - ARI: 8 to 14.5")

    chapter_metrics: list[ChapterMetrics] = []
    for relative_path in CHAPTER_FILES:
        chapter_path = MANUSCRIPT / relative_path
        chapter_metrics.append(compute_metrics(chapter_path))

    warn_count = 0

    for item in chapter_metrics:
        s_fre = status(item.flesch_reading_ease, 17, 100, reverse=True)
        s_fk = status(item.fk_grade, 8, 14)
        s_fog = status(item.gunning_fog, 10, 17.5)
        s_smog = status(item.smog, 10, 15.5)
        s_ari = status(item.ari, 8, 14.5)

        chapter_warns = [s for s in [s_fre, s_fk, s_fog, s_smog, s_ari] if s == "WARN"]
        warn_count += len(chapter_warns)

        print(f"\n{item.chapter}")
        print(
            f"  FRE {item.flesch_reading_ease:>6} [{s_fre}] | "
            f"FK {item.fk_grade:>5} [{s_fk}] | "
            f"Fog {item.gunning_fog:>5} [{s_fog}] | "
            f"SMOG {item.smog:>5} [{s_smog}] | "
            f"ARI {item.ari:>5} [{s_ari}]"
        )

    total_words = sum(m.words for m in chapter_metrics)
    total_sentences = sum(m.sentences for m in chapter_metrics)
    total_syllables = sum(m.syllables for m in chapter_metrics)
    total_complex = sum(m.complex_words for m in chapter_metrics)
    total_characters = sum(m.characters for m in chapter_metrics)

    asl = total_words / max(1, total_sentences)
    asw = total_syllables / max(1, total_words)
    fre = 206.835 - 1.015 * asl - 84.6 * asw
    fk = 0.39 * asl + 11.8 * asw - 15.59
    fog = 0.4 * (asl + 100 * (total_complex / max(1, total_words)))
    smog = 1.043 * math.sqrt(total_complex * (30 / max(1, total_sentences))) + 3.1291
    ari = 4.71 * (total_characters / max(1, total_words)) + 0.5 * asl - 21.43

    print("\n" + "-" * 68)
    print("BOOK-LEVEL SUMMARY")
    print("-" * 68)
    print(f"Words: {total_words:,} | Sentences: {total_sentences:,}")
    print(f"FRE: {fre:.2f} | FK: {fk:.2f} | Fog: {fog:.2f} | SMOG: {smog:.2f} | ARI: {ari:.2f}")

    if warn_count == 0:
        print("\nRESULT: PASS (all readability checkpoints within targets)")
        return 0

    print(f"\nRESULT: WARN ({warn_count} chapter-level metric warnings)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
