#!/bin/bash
cd "$(dirname "$0")"

pandoc \
  manuscript/00_front_matter.md \
  manuscript/part1/ch01_why_big_teams.md \
  manuscript/chapter_gap_all_formats.md \
  manuscript/part1/ch02_end_of_linear_scaling.md \
  manuscript/chapter_gap_all_formats.md \
  manuscript/part1/ch03_what_ai_changes.md \
  manuscript/chapter_gap_all_formats.md \
  manuscript/part2/ch04_headcount_to_leverage.md \
  manuscript/chapter_gap_all_formats.md \
  manuscript/part2/ch05_why_six.md \
  manuscript/chapter_gap_all_formats.md \
  manuscript/part2/ch06_six_core_roles.md \
  manuscript/chapter_gap_all_formats.md \
  manuscript/part2/ch07_human_judgment.md \
  manuscript/chapter_gap_all_formats.md \
  manuscript/part2/ch08_designing_speed.md \
  manuscript/chapter_gap_all_formats.md \
  manuscript/part3/ch09_rapid_prototyping.md \
  manuscript/chapter_gap_all_formats.md \
  manuscript/part3/ch10_decision_making.md \
  manuscript/chapter_gap_all_formats.md \
  manuscript/part3/ch11_small_teams.md \
  manuscript/chapter_gap_all_formats.md \
  manuscript/part3/ch12_ai_xr_frontier.md \
  manuscript/chapter_gap_all_formats.md \
  manuscript/part4/ch13_leadership.md \
  manuscript/chapter_gap_all_formats.md \
  manuscript/part4/ch14_burnout.md \
  manuscript/chapter_gap_all_formats.md \
  manuscript/part4/ch15_when_to_hire.md \
  manuscript/chapter_gap_all_formats.md \
  manuscript/part4/ch16_scaling.md \
  manuscript/chapter_gap_all_formats.md \
  manuscript/back_matter.md \
  manuscript/back_cover_page.md \
  --metadata-file=manuscript/metadata.yaml \
  --css=manuscript/epub.css \
  --resource-path=manuscript \
  --split-level=2 \
  --toc \
  --toc-depth=2 \
  -o output/SmallTeamsStrongSystems.epub

echo "EPUB exit code: $?"

pandoc \
  manuscript/00_front_matter.md \
  manuscript/part1/ch01_why_big_teams.md \
  manuscript/chapter_gap_all_formats.md \
  manuscript/part1/ch02_end_of_linear_scaling.md \
  manuscript/chapter_gap_all_formats.md \
  manuscript/part1/ch03_what_ai_changes.md \
  manuscript/chapter_gap_all_formats.md \
  manuscript/part2/ch04_headcount_to_leverage.md \
  manuscript/chapter_gap_all_formats.md \
  manuscript/part2/ch05_why_six.md \
  manuscript/chapter_gap_all_formats.md \
  manuscript/part2/ch06_six_core_roles.md \
  manuscript/chapter_gap_all_formats.md \
  manuscript/part2/ch07_human_judgment.md \
  manuscript/chapter_gap_all_formats.md \
  manuscript/part2/ch08_designing_speed.md \
  manuscript/chapter_gap_all_formats.md \
  manuscript/part3/ch09_rapid_prototyping.md \
  manuscript/chapter_gap_all_formats.md \
  manuscript/part3/ch10_decision_making.md \
  manuscript/chapter_gap_all_formats.md \
  manuscript/part3/ch11_small_teams.md \
  manuscript/chapter_gap_all_formats.md \
  manuscript/part3/ch12_ai_xr_frontier.md \
  manuscript/chapter_gap_all_formats.md \
  manuscript/part4/ch13_leadership.md \
  manuscript/chapter_gap_all_formats.md \
  manuscript/part4/ch14_burnout.md \
  manuscript/chapter_gap_all_formats.md \
  manuscript/part4/ch15_when_to_hire.md \
  manuscript/chapter_gap_all_formats.md \
  manuscript/part4/ch16_scaling.md \
  manuscript/chapter_gap_all_formats.md \
  manuscript/back_matter.md \
  manuscript/back_cover_page.md \
  --metadata-file=manuscript/metadata.yaml \
  --resource-path=manuscript \
  -o output/SmallTeamsStrongSystems.docx

echo "DOCX exit code: $?"

ls -lh output/
