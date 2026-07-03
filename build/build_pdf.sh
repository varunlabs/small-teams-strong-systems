#!/bin/bash
set -e
cd "$(dirname "$0")/.."

BASE="manuscript"
OUT="drafts/v2"

mkdir -p "$OUT"
echo "Building PDF..."

pandoc \
  --metadata-file="$BASE/metadata.yaml" \
  "$BASE/front_matter.md" \
  "$BASE/part1/ch01_why_big_teams.md" \
  "$BASE/chapter_gap.md" \
  "$BASE/part1/ch02_end_of_linear_scaling.md" \
  "$BASE/chapter_gap.md" \
  "$BASE/part1/ch03_what_ai_changes.md" \
  "$BASE/chapter_gap.md" \
  "$BASE/part2/ch04_headcount_to_leverage.md" \
  "$BASE/chapter_gap.md" \
  "$BASE/part2/ch05_why_six.md" \
  "$BASE/chapter_gap.md" \
  "$BASE/part2/ch06_six_core_roles.md" \
  "$BASE/chapter_gap.md" \
  "$BASE/part2/ch07_human_judgment.md" \
  "$BASE/chapter_gap.md" \
  "$BASE/part2/ch08_designing_speed.md" \
  "$BASE/chapter_gap.md" \
  "$BASE/part3/ch09_rapid_prototyping.md" \
  "$BASE/chapter_gap.md" \
  "$BASE/part3/ch10_decision_making.md" \
  "$BASE/chapter_gap.md" \
  "$BASE/part3/ch11_small_teams.md" \
  "$BASE/chapter_gap.md" \
  "$BASE/part3/ch12_ai_xr_frontier.md" \
  "$BASE/chapter_gap.md" \
  "$BASE/part4/ch13_leadership.md" \
  "$BASE/chapter_gap.md" \
  "$BASE/part4/ch14_burnout.md" \
  "$BASE/chapter_gap.md" \
  "$BASE/part4/ch15_when_to_hire.md" \
  "$BASE/chapter_gap.md" \
  "$BASE/part4/ch16_scaling.md" \
  "$BASE/chapter_gap.md" \
  "$BASE/back_matter.md" \
  --from markdown+raw_tex+raw_attribute \
  --to pdf \
  --pdf-engine=xelatex \
  -M toc=false \
  -V papersize=a5 \
  -V fontsize=11pt \
  -V linestretch=1.45 \
  -V geometry:top=25mm,bottom=25mm,left=22mm,right=22mm \
  -V mainfont="Georgia" \
  -V sansfont="Helvetica Neue" \
  -V monofont="Courier New" \
  -V documentclass=book \
  -V secnumdepth=0 \
  -V numbersections=false \
  -V colorlinks=true \
  -V linkcolor=black \
  -V urlcolor=black \
  -V toccolor=black \
  --syntax-highlighting=tango \
  -o "$OUT/SmallTeamsStrongSystems-v2.pdf"

echo "PDF written to: $OUT/SmallTeamsStrongSystems-v2.pdf"
ls -lh "$OUT/SmallTeamsStrongSystems-v2.pdf"


