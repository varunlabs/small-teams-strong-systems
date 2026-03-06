#!/usr/bin/env python3
"""Redesign all manuscript figures as conceptual, non-table illustrations.

This script parses chapter markdown files for:
- Figure headings: > **Figure X.Y — Title**
- The linked image path for each heading

It then redraws each referenced PNG using meaningful visual motifs selected
from the figure title keywords.
"""

from __future__ import annotations

import math
import random
import re
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT_DIR = ROOT / "manuscript"

FIGURE_HEADING_RE = re.compile(r"\*\*Figure\s+(\d+)\.(\d+)\s+[—-]\s+(.+?)\*\*")
IMAGE_LINK_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")

INK = (20, 28, 42)
SUBTLE = (108, 118, 132)
LIGHT = (223, 232, 244)
PAPER = (255, 255, 255)
ACCENT_A = (56, 105, 188)
ACCENT_B = (46, 164, 111)
ACCENT_C = (209, 124, 57)
ACCENT_D = (151, 97, 208)


@dataclass(frozen=True)
class FigureSpec:
    major: int
    minor: int
    title: str
    target: Path


@dataclass(frozen=True)
class Canvas:
    width: int = 1800
    height: int = 980
    margin: int = 120


def get_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates: list[str] = []
    if bold:
        candidates += [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/Library/Fonts/Arial Bold.ttf",
            "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf",
        ]
    candidates += [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttf",
    ]
    for font_path in candidates:
        try:
            return ImageFont.truetype(font_path, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def add_border(image: Image.Image) -> Image.Image:
    border = max(18, int(min(image.size) * 0.012))
    canvas = Image.new("RGB", (image.width + border * 2, image.height + border * 2), PAPER)
    canvas.paste(image, (border, border))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([0, 0, canvas.width - 1, canvas.height - 1], outline=LIGHT, width=3)
    return canvas


def parse_figure_specs() -> list[FigureSpec]:
    specs: list[FigureSpec] = []
    markdown_files = sorted(MANUSCRIPT_DIR.glob("part*/ch*.md"))

    for markdown_path in markdown_files:
        lines = markdown_path.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            heading_match = FIGURE_HEADING_RE.search(line)
            if not heading_match:
                continue

            major = int(heading_match.group(1))
            minor = int(heading_match.group(2))
            title = heading_match.group(3).strip()

            target_path: Path | None = None
            for follow_index in range(index + 1, min(len(lines), index + 20)):
                image_match = IMAGE_LINK_RE.search(lines[follow_index])
                if not image_match:
                    continue
                raw_target = image_match.group(1).strip().split()[0]
                if raw_target.startswith("manuscript/"):
                    target_path = ROOT / raw_target
                else:
                    target_path = markdown_path.parent / raw_target
                break

            if target_path is None:
                continue

            specs.append(FigureSpec(major=major, minor=minor, title=title, target=target_path))

    return specs


def draw_arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color: tuple[int, int, int], width: int = 5):
    draw.line([start, end], fill=color, width=width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    head_len = 18
    left = (
        int(end[0] - head_len * math.cos(angle - math.pi / 6)),
        int(end[1] - head_len * math.sin(angle - math.pi / 6)),
    )
    right = (
        int(end[0] - head_len * math.cos(angle + math.pi / 6)),
        int(end[1] - head_len * math.sin(angle + math.pi / 6)),
    )
    draw.polygon([end, left, right], fill=color)


def draw_node(draw: ImageDraw.ImageDraw, center: tuple[int, int], radius: int, fill: tuple[int, int, int], outline: tuple[int, int, int] = INK):
    cx, cy = center
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=fill, outline=outline, width=3)


def draw_title(draw: ImageDraw.ImageDraw, spec: FigureSpec, canvas: Canvas):
    title_font = get_font(44, bold=True)
    sub_font = get_font(26)
    title_text = f"Figure {spec.major}.{spec.minor}"
    draw.text((canvas.margin, 62), title_text, font=title_font, fill=INK)
    draw.text((canvas.margin + 290, 72), spec.title, font=sub_font, fill=SUBTLE)


def motif_converging_paths(draw: ImageDraw.ImageDraw, canvas: Canvas, rng: random.Random):
    y_mid = canvas.height // 2 + 40
    left_x = canvas.margin + 30
    right_x = canvas.width - canvas.margin - 30
    join_x = canvas.width // 2 - 120

    offsets = [-190, -80, 25, 135]
    for index, offset in enumerate(offsets):
        y = y_mid + offset
        color = [ACCENT_A, ACCENT_B, ACCENT_C, ACCENT_D][index % 4]
        draw_arrow(draw, (left_x, y), (join_x, y_mid + int(offset * 0.15)), color, width=6)

    draw_node(draw, (join_x + 110, y_mid), 36, (239, 245, 254))
    draw_arrow(draw, (join_x + 150, y_mid), (right_x - 220, y_mid), INK, width=7)

    for ring in range(3):
        rx = right_x - 180 + ring * 60
        draw_node(draw, (rx, y_mid), 25 + ring * 3, (246, 250, 255), outline=ACCENT_A)


def motif_feedback_loop(draw: ImageDraw.ImageDraw, canvas: Canvas, rng: random.Random):
    center = (canvas.width // 2, canvas.height // 2 + 40)
    radius_x = 430
    radius_y = 220

    points = [
        (center[0], center[1] - radius_y),
        (center[0] + radius_x, center[1]),
        (center[0], center[1] + radius_y),
        (center[0] - radius_x, center[1]),
    ]
    labels = [ACCENT_A, ACCENT_B, ACCENT_C, ACCENT_D]

    for idx in range(len(points)):
        start = points[idx]
        end = points[(idx + 1) % len(points)]
        draw_arrow(draw, start, end, labels[idx], width=6)

    for idx, point in enumerate(points):
        draw_node(draw, point, 42, (247, 250, 255), outline=labels[idx])

    draw.ellipse(
        [center[0] - radius_x + 120, center[1] - radius_y + 80, center[0] + radius_x - 120, center[1] + radius_y - 80],
        outline=LIGHT,
        width=3,
    )


def motif_network_tension(draw: ImageDraw.ImageDraw, canvas: Canvas, rng: random.Random):
    network_nodes: list[tuple[int, int]] = []
    rows = 3
    cols = 5
    x0 = canvas.margin + 180
    y0 = 250
    cell_w = 290
    cell_h = 190

    for row in range(rows):
        for col in range(cols):
            jitter_x = rng.randint(-26, 26)
            jitter_y = rng.randint(-22, 22)
            network_nodes.append((x0 + col * cell_w + jitter_x, y0 + row * cell_h + jitter_y))

    for first in range(len(network_nodes)):
        for second in range(first + 1, len(network_nodes)):
            x1, y1 = network_nodes[first]
            x2, y2 = network_nodes[second]
            distance = math.hypot(x2 - x1, y2 - y1)
            if distance > 330:
                continue
            color = LIGHT
            width = 3
            if 160 < distance < 230 and rng.random() > 0.7:
                color = ACCENT_C
                width = 4
            draw.line([(x1, y1), (x2, y2)], fill=color, width=width)

    for idx, center in enumerate(network_nodes):
        palette = ACCENT_A if idx % 3 == 0 else ACCENT_B if idx % 3 == 1 else (236, 243, 254)
        draw_node(draw, center, 20 + (idx % 2) * 4, palette)


def motif_trajectory_shift(draw: ImageDraw.ImageDraw, canvas: Canvas, rng: random.Random):
    left = canvas.margin + 80
    right = canvas.width - canvas.margin - 60
    top = 230
    bottom = canvas.height - 180

    draw.line([(left, bottom), (left, top)], fill=INK, width=4)
    draw.line([(left, bottom), (right, bottom)], fill=INK, width=4)

    split_x = int(left + (right - left) * 0.57)
    draw.line([(split_x, top + 10), (split_x, bottom - 8)], fill=SUBTLE, width=4)

    pre_points: list[tuple[int, int]] = []
    post_points: list[tuple[int, int]] = []

    for step in range(160):
        position = step / 159
        px = int(left + position * (right - left))
        if px <= split_x:
            value = 0.2 + 0.65 * math.sin(position * math.pi * 0.9)
            py = int(bottom - value * (bottom - top) * 0.85)
            pre_points.append((px, py))
        else:
            tail = (px - split_x) / max(1, right - split_x)
            value = 0.72 - 0.28 * tail + 0.05 * math.sin(8 * tail)
            py = int(bottom - value * (bottom - top) * 0.85)
            post_points.append((px, py))

    if len(pre_points) > 1:
        draw.line(pre_points, fill=ACCENT_A, width=6)
    if len(post_points) > 1:
        draw.line(post_points, fill=ACCENT_C, width=6)

    draw_arrow(draw, (left + 20, bottom - 30), (left + 180, bottom - 30), INK, width=4)


def motif_signal_filter(draw: ImageDraw.ImageDraw, canvas: Canvas, rng: random.Random):
    top = 220
    bottom = canvas.height - 170
    left = canvas.margin + 40
    right = canvas.width - canvas.margin - 40

    gate_left = canvas.width // 2 - 80
    gate_right = canvas.width // 2 + 80

    draw.polygon([(gate_left, top), (gate_right, top + 80), (gate_right, bottom - 80), (gate_left, bottom)], outline=INK, fill=(246, 250, 255), width=4)

    for _ in range(120):
        x = rng.randint(left, gate_left - 30)
        y = rng.randint(top, bottom)
        radius = rng.randint(4, 10)
        color = ACCENT_C if rng.random() > 0.7 else LIGHT
        draw_node(draw, (x, y), radius, color, outline=SUBTLE)

    for _ in range(54):
        x = rng.randint(gate_right + 40, right)
        y = rng.randint(top + 40, bottom - 40)
        radius = rng.randint(7, 12)
        color = ACCENT_B if rng.random() > 0.4 else ACCENT_A
        draw_node(draw, (x, y), radius, color)

    draw_arrow(draw, (left + 40, (top + bottom) // 2), (gate_left - 20, (top + bottom) // 2), SUBTLE, width=5)
    draw_arrow(draw, (gate_right + 20, (top + bottom) // 2), (right - 10, (top + bottom) // 2), INK, width=6)


def motif_balance_tradeoff(draw: ImageDraw.ImageDraw, canvas: Canvas, rng: random.Random):
    pivot_x = canvas.width // 2
    pivot_y = canvas.height // 2 + 110

    draw.polygon([(pivot_x, pivot_y - 130), (pivot_x - 70, pivot_y), (pivot_x + 70, pivot_y)], fill=(243, 248, 255), outline=INK)
    beam_left = (pivot_x - 470, pivot_y - 90)
    beam_right = (pivot_x + 470, pivot_y - 30)
    draw.line([beam_left, beam_right], fill=INK, width=8)

    left_plate = (beam_left[0], beam_left[1] + 140)
    right_plate = (beam_right[0], beam_right[1] + 140)
    draw.line([beam_left, left_plate], fill=SUBTLE, width=4)
    draw.line([beam_right, right_plate], fill=SUBTLE, width=4)

    draw.rounded_rectangle([left_plate[0] - 120, left_plate[1], left_plate[0] + 120, left_plate[1] + 34], radius=10, fill=(236, 243, 254), outline=ACCENT_A, width=3)
    draw.rounded_rectangle([right_plate[0] - 120, right_plate[1], right_plate[0] + 120, right_plate[1] + 34], radius=10, fill=(255, 244, 234), outline=ACCENT_C, width=3)

    for idx in range(5):
        draw_node(draw, (left_plate[0] - 70 + idx * 35, left_plate[1] - 34), 10, ACCENT_A)
    for idx in range(7):
        draw_node(draw, (right_plate[0] - 95 + idx * 30, right_plate[1] - 34), 10, ACCENT_C)


def motif_ladder_growth(draw: ImageDraw.ImageDraw, canvas: Canvas, rng: random.Random):
    left = canvas.margin + 130
    bottom = canvas.height - 180
    step_w = 230
    step_h = 95

    for step in range(6):
        x0 = left + step * step_w
        y0 = bottom - step * step_h
        x1 = x0 + step_w
        y1 = y0 + step_h
        fill = (245, 249, 255) if step % 2 == 0 else (236, 244, 255)
        draw.rectangle([x0, y0, x1, y1], fill=fill, outline=LIGHT, width=3)

        marker_x = x0 + int(step_w * 0.55)
        marker_y = y0 - 35
        draw_arrow(draw, (marker_x - 40, marker_y + 30), (marker_x + 35, marker_y), ACCENT_B if step > 2 else ACCENT_A, width=5)

    draw.line([(left - 90, bottom + 90), (left + 6 * step_w + 35, bottom - 6 * step_h - 35)], fill=INK, width=5)


def motif_orbit_system(draw: ImageDraw.ImageDraw, canvas: Canvas, rng: random.Random):
    cx = canvas.width // 2
    cy = canvas.height // 2 + 40

    ring_sizes = [120, 220, 320]
    for ring in ring_sizes:
        draw.ellipse([cx - ring, cy - ring * 0.68, cx + ring, cy + ring * 0.68], outline=LIGHT, width=4)

    draw_node(draw, (cx, cy), 44, ACCENT_A)

    orbit_colors = [ACCENT_B, ACCENT_C, ACCENT_D, (84, 142, 221), (117, 184, 131), (213, 146, 74)]
    for idx in range(12):
        ring = ring_sizes[idx % len(ring_sizes)]
        angle = (2 * math.pi * idx / 12.0) + rng.uniform(-0.2, 0.2)
        x = int(cx + math.cos(angle) * ring)
        y = int(cy + math.sin(angle) * ring * 0.68)
        draw_node(draw, (x, y), 16 if idx % 3 else 21, orbit_colors[idx % len(orbit_colors)])
        if idx % 2 == 0:
            draw.line([(cx, cy), (x, y)], fill=LIGHT, width=2)


def choose_motif(title: str, major: int, minor: int) -> str:
    lowered = title.lower()

    motif_keywords: list[tuple[str, tuple[str, ...]]] = [
        ("feedback_loop", ("feedback", "loop", "latency", "momentum", "iter", "prototype", "learning")),
        ("signal_filter", ("signal", "judgment", "filter", "diagnostic", "boundary", "curation", "traceability", "explanation")),
        ("network_tension", ("team", "roles", "coordination", "ownership", "leadership", "coherence", "context", "system")),
        ("trajectory_shift", ("time", "stability", "shift", "scaling", "speed", "performance", "breakdown", "sustainable")),
        ("balance_tradeoff", (" vs ", "versus", "fragility", "risk", "mistake", "comfort", "trade")),
        ("ladder_growth", ("growth", "amplification", "leverage", "designing", "structural", "headcount")),
        ("converging_paths", ("constraint", "doctrine", "decision", "path", "lens", "from", "why")),
        ("orbit_system", ("interlocking", "variable", "integrity", "forces", "sensitivity")),
    ]

    for motif_name, keywords in motif_keywords:
        if any(keyword in lowered for keyword in keywords):
            return motif_name

    fallback = [
        "converging_paths",
        "feedback_loop",
        "network_tension",
        "trajectory_shift",
        "signal_filter",
        "balance_tradeoff",
        "ladder_growth",
        "orbit_system",
    ]
    return fallback[(major * 17 + minor * 7) % len(fallback)]


def render_figure(spec: FigureSpec):
    canvas = Canvas()
    image = Image.new("RGB", (canvas.width, canvas.height), PAPER)
    draw = ImageDraw.Draw(image)
    rng = random.Random(f"{spec.major}.{spec.minor}:{spec.title}")

    draw_title(draw, spec, canvas)

    motif_name = choose_motif(spec.title, spec.major, spec.minor)
    motifs = {
        "converging_paths": motif_converging_paths,
        "feedback_loop": motif_feedback_loop,
        "network_tension": motif_network_tension,
        "trajectory_shift": motif_trajectory_shift,
        "signal_filter": motif_signal_filter,
        "balance_tradeoff": motif_balance_tradeoff,
        "ladder_growth": motif_ladder_growth,
        "orbit_system": motif_orbit_system,
    }

    motifs[motif_name](draw, canvas, rng)

    # Footer motif marker to keep visual consistency and reduce ambiguity.
    footer_font = get_font(22)
    draw.text((canvas.margin, canvas.height - 62), f"Concept motif: {motif_name.replace('_', ' ')}", font=footer_font, fill=SUBTLE)

    bordered = add_border(image)
    spec.target.parent.mkdir(parents=True, exist_ok=True)
    bordered.save(spec.target, format="PNG", optimize=True)


def main() -> int:
    specs = parse_figure_specs()
    if not specs:
        raise SystemExit("No figure specs found in manuscript markdown")

    for spec in specs:
        render_figure(spec)

    print(f"Redesigned {len(specs)} figures into meaningful conceptual illustrations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
