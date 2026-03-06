#!/usr/bin/env python3
"""Final review of all editorial changes."""
from pathlib import Path
import os, re

ROOT = Path(__file__).resolve().parents[2]
BASE = str(ROOT / 'manuscript')

CHAPTERS = [
    ('part1/ch01_why_big_teams.md', 'Bell Labs'),
    ('part1/ch02_end_of_linear_scaling.md', 'Nokia'),
    ('part1/ch03_what_ai_changes.md', 'Midjourney'),
    ('part2/ch04_headcount_to_leverage.md', 'WhatsApp'),
    ('part2/ch05_why_six.md', 'Amazon'),
    ('part2/ch06_six_core_roles.md', 'Spotify'),
    ('part2/ch07_human_judgment.md', 'Boeing'),
    ('part2/ch08_designing_speed.md', 'Amazon'),
    ('part3/ch09_rapid_prototyping.md', 'Instagram'),
    ('part3/ch10_decision_making.md', 'Netflix'),
    ('part3/ch11_small_teams.md', 'Instagram'),
    ('part3/ch12_ai_xr_frontier.md', 'Beat Saber'),
    ('part4/ch13_leadership.md', 'Valve'),
    ('part4/ch14_burnout.md', 'Atari'),
    ('part4/ch15_when_to_hire.md', 'Basecamp'),
    ('part4/ch16_scaling.md', 'Spotify'),
]

PERSONAL_NOTES = [
    ('part1/ch01_why_big_teams.md', 'A note from the author'),
    ('part2/ch04_headcount_to_leverage.md', 'A note from the author'),
    ('part3/ch09_rapid_prototyping.md', 'A note from the author'),
    ('part4/ch13_leadership.md', 'A note from the author'),
]

IQ_PATTERN = re.compile(r'^\*[A-Z*].*\?[*]?\*$', re.MULTILINE)

print("=" * 60)
print("FINAL EDITORIAL REVIEW")
print("=" * 60)

# 1. Concrete examples
print("\n1. CONCRETE EXAMPLES (1 per chapter)")
all_ok = True
for path, keyword in CHAPTERS:
    with open(os.path.join(BASE, path), encoding='utf-8') as f:
        c = f.read()
    ok = keyword in c
    status = "✓" if ok else "✗ MISSING"
    if not ok:
        all_ok = False
    print(f"   {status:12} {path.split('/')[-1][:35]} [{keyword}]")
print(f"   {'ALL PRESENT' if all_ok else 'SOME MISSING'}")

# 2. Personal notes (1 per Part)
print("\n2. PERSONAL AUTHOR NOTES (1 per Part)")
for path, keyword in PERSONAL_NOTES:
    with open(os.path.join(BASE, path), encoding='utf-8') as f:
        c = f.read()
    ok = keyword in c
    status = "✓" if ok else "✗ MISSING"
    print(f"   {status} {path.split('/')[-1][:40]}")

# 3. Six Forces Framework
print("\n3. PROPRIETARY FRAMEWORK")
framework_files = []
for ch, _ in CHAPTERS:
    with open(os.path.join(BASE, ch), encoding='utf-8') as f:
        c = f.read()
    if 'Six Forces Framework' in c:
        framework_files.append(ch.split('/')[-1])
print(f"   'Six Forces Framework' found in: {', '.join(framework_files)}")

# 4. Italic question count
print("\n4. ITALIC QUESTION REDUCTION")
total_iq = 0
for ch, _ in CHAPTERS:
    with open(os.path.join(BASE, ch), encoding='utf-8') as f:
        c = f.read()
    count = len(IQ_PATTERN.findall(c))
    total_iq += count
    if count > 4:
        print(f"   WARNING: {ch.split('/')[-1]} has {count} italic questions")
print(f"   Total italic questions: {total_iq} (target: ~40)")

# 5. Vocabulary counts
print("\n5. VOCABULARY FREQUENCY CHECK")
combined = ""
for ch, _ in CHAPTERS:
    with open(os.path.join(BASE, ch), encoding='utf-8') as f:
        combined += f.read()
for word in ['system', 'structural', 'decisions', 'architectural', 'foundational', 'choices', 'tradeoffs']:
    count = len(re.findall(r'\b' + word + r'\b', combined, re.IGNORECASE))
    print(f"   '{word}': {count}×")

# 6. Punchy sentences check
print("\n6. PUNCHY SENTENCE SAMPLES (first short sentence per chapter)")
punchy_checks = [
    ('part1/ch01_why_big_teams.md', 'Scale looked like strength'),
    ('part1/ch03_what_ai_changes.md', 'Seductive, expensive'),
    ('part2/ch05_why_six.md', 'Safe and slow'),
    ('part2/ch07_human_judgment.md', 'One scales. The other'),
    ('part3/ch09_rapid_prototyping.md', 'Discover fast'),
    ('part3/ch11_small_teams.md', 'Short chains'),
    ('part4/ch14_burnout.md', 'points to a broken design'),
    ('part4/ch16_scaling.md', 'Expansion is the easy part'),
]
for path, snippet in punchy_checks:
    with open(os.path.join(BASE, path), encoding='utf-8') as f:
        c = f.read()
    ok = snippet in c
    print(f"   {'✓' if ok else '✗'} {path.split('/')[-1][:35]}: '{snippet}'")

# 7. Word count
print("\n7. MANUSCRIPT STATS")
words = len(re.findall(r'\w+', combined))
print(f"   Total word count: ~{words:,}")
print(f"   Chapters: 16")

print("\n" + "=" * 60)
print("REVIEW COMPLETE")
print("=" * 60)
