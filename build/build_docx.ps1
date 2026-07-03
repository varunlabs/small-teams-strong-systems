# Build DOCX for "Small Teams, Strong Systems"
$ErrorActionPreference = "Stop"

$ROOT = "$PSScriptRoot\.."
$OUT  = "$ROOT\published\v2"

New-Item -ItemType Directory -Force $OUT | Out-Null
Write-Host "Building DOCX..."

$docxArgs = @(
  "$ROOT\manuscript\front_matter.md",
  "$ROOT\manuscript\part1\ch01_why_big_teams.md",
  "$ROOT\manuscript\chapter_gap_all_formats.md",
  "$ROOT\manuscript\part1\ch02_end_of_linear_scaling.md",
  "$ROOT\manuscript\chapter_gap_all_formats.md",
  "$ROOT\manuscript\part1\ch03_what_ai_changes.md",
  "$ROOT\manuscript\chapter_gap_all_formats.md",
  "$ROOT\manuscript\part2\ch04_headcount_to_leverage.md",
  "$ROOT\manuscript\chapter_gap_all_formats.md",
  "$ROOT\manuscript\part2\ch05_why_six.md",
  "$ROOT\manuscript\chapter_gap_all_formats.md",
  "$ROOT\manuscript\part2\ch06_six_core_roles.md",
  "$ROOT\manuscript\chapter_gap_all_formats.md",
  "$ROOT\manuscript\part2\ch07_human_judgment.md",
  "$ROOT\manuscript\chapter_gap_all_formats.md",
  "$ROOT\manuscript\part2\ch08_designing_speed.md",
  "$ROOT\manuscript\chapter_gap_all_formats.md",
  "$ROOT\manuscript\part3\ch09_rapid_prototyping.md",
  "$ROOT\manuscript\chapter_gap_all_formats.md",
  "$ROOT\manuscript\part3\ch10_decision_making.md",
  "$ROOT\manuscript\chapter_gap_all_formats.md",
  "$ROOT\manuscript\part3\ch11_small_teams.md",
  "$ROOT\manuscript\chapter_gap_all_formats.md",
  "$ROOT\manuscript\part3\ch12_ai_xr_frontier.md",
  "$ROOT\manuscript\chapter_gap_all_formats.md",
  "$ROOT\manuscript\part4\ch13_leadership.md",
  "$ROOT\manuscript\chapter_gap_all_formats.md",
  "$ROOT\manuscript\part4\ch14_burnout.md",
  "$ROOT\manuscript\chapter_gap_all_formats.md",
  "$ROOT\manuscript\part4\ch15_when_to_hire.md",
  "$ROOT\manuscript\chapter_gap_all_formats.md",
  "$ROOT\manuscript\part4\ch16_scaling.md",
  "$ROOT\manuscript\chapter_gap_all_formats.md",
  "$ROOT\manuscript\back_matter.md",
  "--metadata-file=$ROOT\manuscript\metadata.yaml",
  "--resource-path=$ROOT\manuscript",
  "-o", "$OUT\SmallTeamsStrongSystems-v2.docx"
)

& pandoc @docxArgs
$exitCode = $LASTEXITCODE

if ($exitCode -eq 0) {
  Write-Host "DOCX built: $OUT\SmallTeamsStrongSystems-v2.docx"
  Get-Item "$OUT\SmallTeamsStrongSystems-v2.docx" | Format-List Length
} else {
  Write-Host "DOCX build failed (exit $exitCode)"
  exit $exitCode
}
