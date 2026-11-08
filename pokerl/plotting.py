"""Dependency-free SVG charts with a consistent dark research-lab theme."""

from __future__ import annotations

import html
import math
from collections.abc import Sequence
from pathlib import Path

BG = "#f7f4ed"
PANEL = "#f1ece1"
GRID = "#d8d0c1"
TEXT = "#201d18"
MUTED = "#746e63"
ACCENT = "#8a5a2b"
VIOLET = "#5b6b8c"
GREEN = "#3f6b4f"
AMBER = "#a67c2e"
RED = "#8a3f32"
SERIES = [ACCENT, VIOLET, GREEN, AMBER, RED, "#7d5a62", "#4f6b72", "#8a7a55"]


def _esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def _frame(width: int, height: int, title: str, subtitle: str = "") -> list[str]:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        f"<title>{_esc(title)}</title>",
        f'<rect width="{width}" height="{height}" fill="{BG}"/>',
        f'<rect x="12" y="12" width="{width - 24}" height="{height - 24}" rx="16" fill="{PANEL}" stroke="{GRID}"/>',
        f'<text x="32" y="48" fill="{TEXT}" font-family="ui-sans-serif,system-ui,sans-serif" font-size="20" font-weight="700">{_esc(title)}</text>',
    ]
    if subtitle:
        parts.append(
            f'<text x="32" y="72" fill="{MUTED}" font-family="ui-monospace,monospace" font-size="12">{_esc(subtitle)}</text>'
        )
    return parts


def _write(path: str | Path, parts: Sequence[str]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(parts) + "\n</svg>\n", encoding="utf-8")


def bar_chart(
    labels: Sequence[str],
    values: Sequence[float],
    *,
    errors: Sequence[tuple[float, float]] | None = None,
    title: str,
    subtitle: str = "",
    xlabel: str = "",
    path: str | Path,
    color: str = ACCENT,
    width: int = 820,
    height: int = 420,
) -> None:
    parts = _frame(width, height, title, subtitle)
    if not values:
        parts.append(
            f'<text x="{width / 2}" y="{height / 2}" text-anchor="middle" fill="{MUTED}" font-size="14">No data yet — run the benchmark.</text>'
        )
        _write(path, parts)
        return
    left = 190
    right = 60
    top = 110
    bottom = 70
    plot_w = width - left - right
    plot_h = height - top - bottom
    max_value = max(max(values), 1e-9)
    lo = min(0.0, min(values))
    hi = max_value * 1.08
    span = max(hi - lo, 1e-9)
    bar_gap = 10
    bar_h = max(14, (plot_h - bar_gap * (len(values) - 1)) / len(values))
    # grid
    for frac in (0, 0.25, 0.5, 0.75, 1.0):
        x = left + frac * plot_w
        value = lo + frac * span
        parts.append(
            f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top + plot_h}" stroke="{GRID}" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{x:.1f}" y="{top + plot_h + 22}" text-anchor="middle" fill="{MUTED}" font-family="ui-monospace,monospace" font-size="11">{value:.1f}</text>'
        )
    for i, (label, value) in enumerate(zip(labels, values)):
        y = top + i * (bar_h + bar_gap)
        x0 = left + (0 - lo) / span * plot_w
        x1 = left + (value - lo) / span * plot_w
        bar_color = color if i == 0 else SERIES[i % len(SERIES)]
        parts.append(
            f'<text x="{left - 12}" y="{y + bar_h * 0.7:.1f}" text-anchor="end" fill="{TEXT}" font-family="ui-sans-serif,system-ui,sans-serif" font-size="13">{_esc(label)}</text>'
        )
        parts.append(
            f'<rect x="{min(x0, x1):.1f}" y="{y:.1f}" width="{max(2, abs(x1 - x0)):.1f}" height="{bar_h:.1f}" rx="4" fill="{bar_color}" opacity="0.9"/>'
        )
        parts.append(
            f'<text x="{max(x0, x1) + 10:.1f}" y="{y + bar_h * 0.7:.1f}" fill="{TEXT}" font-family="ui-monospace,monospace" font-size="12">{value:.1f}</text>'
        )
        if errors is not None and i < len(errors):
            elo, ehi = errors[i]
            ex0 = left + (elo - lo) / span * plot_w
            ex1 = left + (ehi - lo) / span * plot_w
            cy = y + bar_h / 2
            parts.append(
                f'<line x1="{ex0:.1f}" y1="{cy:.1f}" x2="{ex1:.1f}" y2="{cy:.1f}" stroke="{TEXT}" stroke-width="1.4" opacity="0.8"/>'
            )
            parts.append(
                f'<line x1="{ex0:.1f}" y1="{cy - 4:.1f}" x2="{ex0:.1f}" y2="{cy + 4:.1f}" stroke="{TEXT}" stroke-width="1.4" opacity="0.8"/>'
            )
            parts.append(
                f'<line x1="{ex1:.1f}" y1="{cy - 4:.1f}" x2="{ex1:.1f}" y2="{cy + 4:.1f}" stroke="{TEXT}" stroke-width="1.4" opacity="0.8"/>'
            )
    if xlabel:
        parts.append(
            f'<text x="{left + plot_w / 2}" y="{height - 22}" text-anchor="middle" fill="{MUTED}" font-family="ui-sans-serif,system-ui,sans-serif" font-size="12">{_esc(xlabel)}</text>'
        )
    _write(path, parts)


def line_chart(
    series: dict[str, Sequence[tuple[float, float]]],
    *,
    title: str,
    subtitle: str = "",
    xlabel: str = "",
    ylabel: str = "",
    path: str | Path,
    width: int = 820,
    height: int = 420,
    y_min: float | None = None,
    y_max: float | None = None,
) -> None:
    parts = _frame(width, height, title, subtitle)
    all_points = [p for points in series.values() for p in points]
    if not all_points:
        parts.append(
            f'<text x="{width / 2}" y="{height / 2}" text-anchor="middle" fill="{MUTED}" font-size="14">No data yet — run the benchmark.</text>'
        )
        _write(path, parts)
        return
    left, right, top, bottom = 80, 40, 110, 70
    plot_w = width - left - right
    plot_h = height - top - bottom
    xs = [p[0] for p in all_points]
    ys = [p[1] for p in all_points]
    xmin, xmax = min(xs), max(xs)
    ymin = y_min if y_min is not None else min(ys)
    ymax = y_max if y_max is not None else max(ys)
    if xmax == xmin:
        xmax = xmin + 1
    if ymax == ymin:
        ymax = ymin + 1
    pad_y = (ymax - ymin) * 0.08
    ymin -= pad_y
    ymax += pad_y
    for frac in (0, 0.25, 0.5, 0.75, 1.0):
        y = top + plot_h - frac * plot_h
        value = ymin + frac * (ymax - ymin)
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}" stroke="{GRID}"/>')
        parts.append(
            f'<text x="{left - 10}" y="{y + 4:.1f}" text-anchor="end" fill="{MUTED}" font-family="ui-monospace,monospace" font-size="11">{value:.2f}</text>'
        )
    for frac in (0, 0.25, 0.5, 0.75, 1.0):
        x = left + frac * plot_w
        value = xmin + frac * (xmax - xmin)
        parts.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top + plot_h}" stroke="{GRID}" opacity="0.4"/>')
        parts.append(
            f'<text x="{x:.1f}" y="{top + plot_h + 22}" text-anchor="middle" fill="{MUTED}" font-family="ui-monospace,monospace" font-size="11">{value:.0f}</text>'
        )
    for idx, (name, points) in enumerate(series.items()):
        color = SERIES[idx % len(SERIES)]
        coords = []
        for x, y in points:
            px = left + (x - xmin) / (xmax - xmin) * plot_w
            py = top + plot_h - (y - ymin) / (ymax - ymin) * plot_h
            coords.append(f"{px:.1f},{py:.1f}")
        if coords:
            parts.append(
                f'<polyline points="{" ".join(coords)}" fill="none" stroke="{color}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/>'
            )
            for c in coords:
                x, y = c.split(",")
                parts.append(f'<circle cx="{x}" cy="{y}" r="3.2" fill="{color}"/>')
        lx = left + idx * 150
        parts.append(f'<rect x="{lx}" y="{height - 52}" width="14" height="4" rx="2" fill="{color}"/>')
        parts.append(
            f'<text x="{lx + 20}" y="{height - 45}" fill="{MUTED}" font-family="ui-sans-serif,system-ui,sans-serif" font-size="12">{_esc(name)}</text>'
        )
    if xlabel:
        parts.append(
            f'<text x="{left + plot_w / 2}" y="{height - 18}" text-anchor="middle" fill="{MUTED}" font-size="12">{_esc(xlabel)}</text>'
        )
    if ylabel:
        parts.append(
            f'<text x="22" y="{top + plot_h / 2}" transform="rotate(-90 22 {top + plot_h / 2})" text-anchor="middle" fill="{MUTED}" font-size="12">{_esc(ylabel)}</text>'
        )
    _write(path, parts)


def scatter_chart(
    points: Sequence[tuple[float, float, str]],
    *,
    title: str,
    subtitle: str = "",
    xlabel: str = "",
    ylabel: str = "",
    path: str | Path,
    width: int = 820,
    height: int = 440,
) -> None:
    parts = _frame(width, height, title, subtitle)
    if not points:
        parts.append(
            f'<text x="{width / 2}" y="{height / 2}" text-anchor="middle" fill="{MUTED}" font-size="14">No data yet — run the benchmark.</text>'
        )
        _write(path, parts)
        return
    left, right, top, bottom = 90, 50, 110, 70
    plot_w = width - left - right
    plot_h = height - top - bottom
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    xmin, xmax = max(1e-6, min(xs) * 0.8), max(xs) * 1.25
    ymin, ymax = min(ys) - 40, max(ys) + 40
    for frac in (0, 0.25, 0.5, 0.75, 1.0):
        y = top + plot_h - frac * plot_h
        value = ymin + frac * (ymax - ymin)
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}" stroke="{GRID}"/>')
        parts.append(
            f'<text x="{left - 10}" y="{y + 4:.1f}" text-anchor="end" fill="{MUTED}" font-family="ui-monospace,monospace" font-size="11">{value:.0f}</text>'
        )
    for frac in (0, 0.25, 0.5, 0.75, 1.0):
        x = left + frac * plot_w
        value = xmin * (xmax / xmin) ** frac
        parts.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top + plot_h}" stroke="{GRID}" opacity="0.4"/>')
        parts.append(
            f'<text x="{x:.1f}" y="{top + plot_h + 22}" text-anchor="middle" fill="{MUTED}" font-family="ui-monospace,monospace" font-size="11">{value:.0f}</text>'
        )
    for idx, (x, y, label) in enumerate(points):
        px = left + (math.log(max(x, xmin) / xmin) / math.log(xmax / xmin)) * plot_w
        py = top + plot_h - (y - ymin) / (ymax - ymin) * plot_h
        color = SERIES[idx % len(SERIES)]
        parts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="7" fill="{color}" opacity="0.9"/>')
        parts.append(
            f'<text x="{px + 10:.1f}" y="{py - 8:.1f}" fill="{TEXT}" font-family="ui-sans-serif,system-ui,sans-serif" font-size="12">{_esc(label)}</text>'
        )
    if xlabel:
        parts.append(
            f'<text x="{left + plot_w / 2}" y="{height - 20}" text-anchor="middle" fill="{MUTED}" font-size="12">{_esc(xlabel)}</text>'
        )
    if ylabel:
        parts.append(
            f'<text x="24" y="{top + plot_h / 2}" transform="rotate(-90 24 {top + plot_h / 2})" text-anchor="middle" fill="{MUTED}" font-size="12">{_esc(ylabel)}</text>'
        )
    _write(path, parts)


def heatmap(
    row_labels: Sequence[str],
    col_labels: Sequence[str],
    values: Sequence[Sequence[float]],
    *,
    title: str,
    path: str | Path,
    width: int = 820,
    height: int = 460,
) -> None:
    parts = _frame(width, height, title)
    if not values:
        _write(path, parts)
        return
    left, top = 150, 100
    cell_w = (width - left - 30) / max(1, len(col_labels))
    cell_h = (height - top - 40) / max(1, len(row_labels))
    for i, label in enumerate(row_labels):
        parts.append(
            f'<text x="{left - 10}" y="{top + i * cell_h + cell_h / 2 + 4:.1f}" text-anchor="end" fill="{TEXT}" font-size="12">{_esc(label)}</text>'
        )
    for j, label in enumerate(col_labels):
        parts.append(
            f'<text x="{left + j * cell_w + cell_w / 2:.1f}" y="{top - 10}" text-anchor="middle" fill="{MUTED}" font-size="11">{_esc(label)}</text>'
        )
    for i, row in enumerate(values):
        for j, value in enumerate(row):
            intensity = max(0.0, min(1.0, value))
            color = f"rgba(34,211,238,{0.12 + 0.75 * intensity:.3f})"
            x = left + j * cell_w
            y = top + i * cell_h
            parts.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell_w - 4:.1f}" height="{cell_h - 4:.1f}" rx="4" fill="{color}"/>'
            )
            parts.append(
                f'<text x="{x + cell_w / 2:.1f}" y="{y + cell_h / 2 + 4:.1f}" text-anchor="middle" fill="{TEXT}" font-family="ui-monospace,monospace" font-size="12">{value:.2f}</text>'
            )
    _write(path, parts)
