from __future__ import annotations

import math
import os


TYPE_COLORS = {
    "normal": "#A8A878", "fire": "#F08030", "water": "#6890F0", "electric": "#F8D030",
    "grass": "#78C850", "ice": "#98D8D8", "fighting": "#C03028", "poison": "#A040A0",
    "ground": "#E0C068", "flying": "#A890F0", "psychic": "#F85888", "bug": "#A8B820",
    "rock": "#B8A038", "ghost": "#705898", "dragon": "#7038F8", "dark": "#705848",
    "steel": "#B8B8D0", "fairy": "#EE99AC",
}


def generate_radar_chart(stats: dict, clean_name: str, types: list[str] | None = None) -> str:
    """Generate a labelled six-stat radar chart with a type-coloured core."""
    keys = ["hp", "attack", "defense", "speed", "special-defense", "special-attack"]
    labels = ["HP", "ATK", "DEF", "SPE", "SPD", "SPA"]
    values = [stats.get(k, 0) for k in keys]
    max_val = 255
    accent = TYPE_COLORS.get((types or ["poison"])[0], "#6A0DAD")

    size = 240
    center = size / 2
    radius = 82
    angle_step = (2 * math.pi) / 6

    def ring(multipliers) -> str:
        return " ".join(
            f"{center + m * radius * math.cos(i * angle_step - math.pi / 2):.2f},"
            f"{center + m * radius * math.sin(i * angle_step - math.pi / 2):.2f}"
            for i, m in enumerate(multipliers)
        )

    points = ring(v / max_val for v in values)
    grid = []
    for level in (0.25, 0.5, 0.75, 1.0):
        dash = "3 4" if level < 1 else "0"
        grid.append(
            f'<polygon points="{ring([level] * 6)}" fill="none" stroke="#4C3A6B" '
            f'stroke-width="1" stroke-dasharray="{dash}"/>'
        )
    axes = []
    for i in range(6):
        x = center + radius * math.cos(i * angle_step - math.pi / 2)
        y = center + radius * math.sin(i * angle_step - math.pi / 2)
        axes.append(f'<line x1="{center}" y1="{center}" x2="{x:.2f}" y2="{y:.2f}" stroke="#4C3A6B" stroke-width="1"/>')

    text = []
    for i, label in enumerate(labels):
        angle = i * angle_step - math.pi / 2
        x = center + (radius + 22) * math.cos(angle)
        y = center + (radius + 22) * math.sin(angle)
        text.append(
            f'<text x="{x:.2f}" y="{y + 3:.2f}" text-anchor="middle" '
            f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" '
            f'font-size="9" fill="#C4B5FD">{label}</text>'
        )

    svg = f"""<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Base stat radar for {clean_name}">
  <title>{clean_name} base stat radar</title>
  {''.join(grid)}
  {''.join(axes)}
  <polygon points="{points}" fill="{accent}" fill-opacity="0.45" stroke="{accent}" stroke-width="2.5" stroke-linejoin="round"/>
  <circle cx="{center}" cy="{center}" r="2.5" fill="#F5F3FF"/>
  {''.join(text)}
</svg>"""

    os.makedirs("assets", exist_ok=True)
    with open(f"assets/stats_{clean_name}.svg", "w", encoding="utf-8") as f:
        f.write(svg)
