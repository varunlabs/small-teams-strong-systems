# Build PDF for "Small Teams, Strong Systems"
$ErrorActionPreference = "Stop"

$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User") + ";$env:USERPROFILE\AppData\Roaming\Python\Python314\Scripts"

$ROOT = "$PSScriptRoot\.."
$BASE = "$ROOT\manuscript"
$OUT  = "$ROOT\published\v2"

New-Item -ItemType Directory -Force $OUT | Out-Null
Write-Host "Building PDF with XeLaTeX..."

Push-Location $BASE
try {
    $interiorArgs = @(
        "--metadata-file=metadata.yaml",
        "front_matter.md",
        "part1/ch01_why_big_teams.md",
        "chapter_gap.md",
        "part1/ch02_end_of_linear_scaling.md",
        "chapter_gap.md",
        "part1/ch03_what_ai_changes.md",
        "chapter_gap.md",
        "part2/ch04_headcount_to_leverage.md",
        "chapter_gap.md",
        "part2/ch05_why_six.md",
        "chapter_gap.md",
        "part2/ch06_six_core_roles.md",
        "chapter_gap.md",
        "part2/ch07_human_judgment.md",
        "chapter_gap.md",
        "part2/ch08_designing_speed.md",
        "chapter_gap.md",
        "part3/ch09_rapid_prototyping.md",
        "chapter_gap.md",
        "part3/ch10_decision_making.md",
        "chapter_gap.md",
        "part3/ch11_small_teams.md",
        "chapter_gap.md",
        "part3/ch12_ai_xr_frontier.md",
        "chapter_gap.md",
        "part4/ch13_leadership.md",
        "chapter_gap.md",
        "part4/ch14_burnout.md",
        "chapter_gap.md",
        "part4/ch15_when_to_hire.md",
        "chapter_gap.md",
        "part4/ch16_scaling.md",
        "chapter_gap.md",
        "back_matter.md",
        "--to", "pdf",
        "--pdf-engine", "xelatex",
        "--variable", "geometry:a5paper",
        "--variable", "geometry:top=25mm",
        "--variable", "geometry:bottom=25mm",
        "--variable", "geometry:left=22mm",
        "--variable", "geometry:right=22mm",
        "-o", "$OUT\SmallTeamsStrongSystems-v2.pdf"
    )

    & pandoc @interiorArgs
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: PDF build failed (exit $LASTEXITCODE)"
        exit 1
    }
} finally {
    Pop-Location
}

Write-Host "PDF built: $OUT\SmallTeamsStrongSystems-v2.pdf"
Get-Item "$OUT\SmallTeamsStrongSystems-v2.pdf" | Format-List Length
