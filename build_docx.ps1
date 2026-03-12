# Build DOCX for "Small Teams, Strong Systems"
$ErrorActionPreference = "Stop"

$OUT = "output"

Write-Host "Building DOCX..."

$docxArgs = @(
  "$PSScriptRoot\manuscript\cover_pages.md",
  "$PSScriptRoot\manuscript\00_front_matter.md",
  "$PSScriptRoot\manuscript\part1\ch01_why_big_teams.md",
  "$PSScriptRoot\manuscript\chapter_gap_all_formats.md",
  "$PSScriptRoot\manuscript\part1\ch02_end_of_linear_scaling.md",
  "$PSScriptRoot\manuscript\chapter_gap_all_formats.md",
  "$PSScriptRoot\manuscript\part1\ch03_what_ai_changes.md",
  "$PSScriptRoot\manuscript\chapter_gap_all_formats.md",
  "$PSScriptRoot\manuscript\part2\ch04_headcount_to_leverage.md",
  "$PSScriptRoot\manuscript\chapter_gap_all_formats.md",
  "$PSScriptRoot\manuscript\part2\ch05_why_six.md",
  "$PSScriptRoot\manuscript\chapter_gap_all_formats.md",
  "$PSScriptRoot\manuscript\part2\ch06_six_core_roles.md",
  "$PSScriptRoot\manuscript\chapter_gap_all_formats.md",
  "$PSScriptRoot\manuscript\part2\ch07_human_judgment.md",
  "$PSScriptRoot\manuscript\chapter_gap_all_formats.md",
  "$PSScriptRoot\manuscript\part2\ch08_designing_speed.md",
  "$PSScriptRoot\manuscript\chapter_gap_all_formats.md",
  "$PSScriptRoot\manuscript\part3\ch09_rapid_prototyping.md",
  "$PSScriptRoot\manuscript\chapter_gap_all_formats.md",
  "$PSScriptRoot\manuscript\part3\ch10_decision_making.md",
  "$PSScriptRoot\manuscript\chapter_gap_all_formats.md",
  "$PSScriptRoot\manuscript\part3\ch11_small_teams.md",
  "$PSScriptRoot\manuscript\chapter_gap_all_formats.md",
  "$PSScriptRoot\manuscript\part3\ch12_ai_xr_frontier.md",
  "$PSScriptRoot\manuscript\chapter_gap_all_formats.md",
  "$PSScriptRoot\manuscript\part4\ch13_leadership.md",
  "$PSScriptRoot\manuscript\chapter_gap_all_formats.md",
  "$PSScriptRoot\manuscript\part4\ch14_burnout.md",
  "$PSScriptRoot\manuscript\chapter_gap_all_formats.md",
  "$PSScriptRoot\manuscript\part4\ch15_when_to_hire.md",
  "$PSScriptRoot\manuscript\chapter_gap_all_formats.md",
  "$PSScriptRoot\manuscript\part4\ch16_scaling.md",
  "$PSScriptRoot\manuscript\chapter_gap_all_formats.md",
  "$PSScriptRoot\manuscript\back_matter.md",
  "$PSScriptRoot\manuscript\back_cover_page.md",
  "--metadata-file=$PSScriptRoot\manuscript\metadata.yaml",
  "--resource-path=$PSScriptRoot\manuscript",
  "-o",
  "$OUT/SmallTeamsStrongSystems.docx"
)

& pandoc @docxArgs
$exitCode = $LASTEXITCODE

Write-Host "DOCX exit code: $exitCode"

if ($exitCode -eq 0) {
  Write-Host "DOCX built successfully: $OUT/SmallTeamsStrongSystems.docx"
  Get-Item "$OUT/SmallTeamsStrongSystems.docx" | Format-List Length
} else {
  Write-Host "DOCX build failed with exit code $exitCode"
  exit $exitCode
}
