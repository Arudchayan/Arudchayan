from __future__ import annotations

import html
import math
import os


TYPE_COLORS = {
    "normal": "#A8A878", "fire": "#F08030", "water": "#6890F0", "electric": "#F8D030",
    "grass": "#78C850", "ice": "#98D8D8", "fighting": "#C03028", "poison": "#A040A0",
    "ground": "#E0C068", "flying": "#A890F0", "psychic": "#F85888", "bug": "#A8B820",
    "rock": "#B8A038", "ghost": "#705898", "dragon": "#7038F8", "dark": "#705848",
    "steel": "#B8B8D0", "fairy": "#EE99AC",
}

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
STAT_KEYS = ["hp", "attack", "defense", "speed", "special-defense", "special-attack"]
STAT_LABELS = ["HP", "ATK", "DEF", "SPE", "SP.DEF", "SP.ATK"]
RADAR_SCALE = 180


def _type_colors(types: list[str] | None) -> tuple[str, str]:
    types = types or ["normal"]
    primary = TYPE_COLORS.get(types[0], "#8B5CF6")
    secondary = TYPE_COLORS.get(types[1], "#22D3EE") if len(types) > 1 else primary
    return primary, secondary


def _type_chips(types: list[str] | None, right: float, y: float) -> tuple[str, float]:
    """Right-aligned type pills. Returns (svg, left edge x)."""
    chips = []
    x = right
    for raw in reversed(types or ["normal"]):
        t = raw.lower()
        color = TYPE_COLORS.get(t, "#8B5CF6")
        w = 7.4 * len(t) + 18
        x -= w
        chips.append(
            f'<rect x="{x:.2f}" y="{y}" width="{w:.2f}" height="17" rx="8.5" '
            f'fill="{color}" fill-opacity="0.16" stroke="{color}" stroke-opacity="0.75"/>'
            f'<text x="{x + w / 2:.2f}" y="{y + 12:.2f}" text-anchor="middle" '
            f'font-family="{MONO}" font-size="8.5" letter-spacing="1" fill="{color}">{html.escape(t.upper())}</text>'
        )
        x -= 6
    return "".join(chips), x


def generate_radar_chart(stats: dict, clean_name: str, types: list[str] | None = None) -> str:
    """Generate a theme-safe stat card: dark HUD panel with a six-stat radar."""
    values = [min(stats.get(k, 0), RADAR_SCALE) for k in STAT_KEYS]
    display_name = (
        clean_name.replace("-mega", " · MEGA")
        .replace("mega-", "MEGA · ")
        .replace("-", " ")
        .upper()
    )
    primary, secondary = _type_colors(types)

    width, height = 300, 330
    cx, cy, radius = 150, 176, 80
    angle_step = 2 * math.pi / 6

    def point(i: int, r: float) -> tuple[float, float]:
        angle = i * angle_step - math.pi / 2
        return cx + r * math.cos(angle), cy + r * math.sin(angle)

    def ring(mult: float) -> str:
        return " ".join(f"{x:.2f},{y:.2f}" for x, y in (point(i, radius * mult) for i in range(6)))

    polygon = " ".join(
        f"{x:.2f},{y:.2f}" for x, y in (point(i, radius * v / RADAR_SCALE) for i, v in enumerate(values))
    )
    grid = "".join(
        f'<polygon points="{ring(m)}" fill="none" stroke="#FFFFFF" '
        f'stroke-opacity="{0.10 if m < 1 else 0.20}" stroke-width="1" '
        f'stroke-dasharray="{"3 5" if m < 1 else "0"}"/>'
        for m in (0.25, 0.5, 0.75, 1.0)
    )
    axes = "".join(
        f'<line x1="{cx}" y1="{cy}" x2="{x:.2f}" y2="{y:.2f}" stroke="#FFFFFF" stroke-opacity="0.10"/>'
        for x, y in (point(i, radius) for i in range(6))
    )
    dots = "".join(
        f'<circle cx="{x:.2f}" cy="{y:.2f}" r="2.4" fill="#FFFFFF" fill-opacity="0.92"/>'
        for x, y in (point(i, radius * v / RADAR_SCALE) for i, v in enumerate(values))
    )

    labels = []
    for i, (label, value) in enumerate(zip(STAT_LABELS, [stats.get(k, 0) for k in STAT_KEYS])):
        lx, ly = point(i, radius + 27)
        labels.append(
            f'<text x="{lx:.2f}" y="{ly - 3:.2f}" text-anchor="middle" font-family="{MONO}" '
            f'font-size="8" letter-spacing="0.8" fill="#8B87A8">{label}</text>'
            f'<text x="{lx:.2f}" y="{ly + 9:.2f}" text-anchor="middle" font-family="{MONO}" '
            f'font-size="11" font-weight="700" fill="#F4F1FF">{value}</text>'
        )

    chips, _ = _type_chips(types, width - 18, 19)
    top_key = max(stats, key=stats.get) if stats else "hp"
    top_label = dict(zip(STAT_KEYS, STAT_LABELS)).get(top_key, "HP")
    top_value = stats.get(top_key, 0)
    bst = sum(stats.values()) if stats else 0

    svg = f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{html.escape(display_name.title())} base stat radar">
  <title>{html.escape(display_name.title())} base stat radar</title>
  <defs>
    <linearGradient id="card-bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0D0B1A"/>
      <stop offset="1" stop-color="#141026"/>
    </linearGradient>
    <linearGradient id="card-fill" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{primary}" stop-opacity="0.55"/>
      <stop offset="1" stop-color="{secondary}" stop-opacity="0.30"/>
    </linearGradient>
    <linearGradient id="card-stroke" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{primary}"/>
      <stop offset="1" stop-color="{secondary}"/>
    </linearGradient>
    <filter id="card-glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="4" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="18" fill="url(#card-bg)" stroke="#3A2C58"/>
  <rect x="1" y="1" width="{width - 2}" height="2" rx="1" fill="url(#card-stroke)" fill-opacity="0.6"/>
  <text x="18" y="31" font-family="{MONO}" font-size="13" font-weight="700" letter-spacing="2" fill="#F4F1FF">{html.escape(display_name)}</text>
  {chips}
  <line x1="18" y1="46" x2="{width - 18}" y2="46" stroke="#FFFFFF" stroke-opacity="0.07"/>
  {grid}{axes}
  <polygon points="{polygon}" fill="url(#card-fill)" stroke="url(#card-stroke)" stroke-width="2" stroke-linejoin="round" filter="url(#card-glow)"/>
  {dots}
  {''.join(labels)}
  <text x="18" y="{height - 16}" font-family="{MONO}" font-size="9" letter-spacing="1.2" fill="#6F6A88">BST</text>
  <text x="50" y="{height - 16}" font-family="{MONO}" font-size="13" font-weight="700" fill="#F4F1FF">{bst}</text>
  <text x="{width - 18}" y="{height - 16}" text-anchor="end" font-family="{MONO}" font-size="9" letter-spacing="1.1" fill="#6F6A88">{top_label} · {top_value}</text>
</svg>"""

    os.makedirs("assets", exist_ok=True)
    with open(f"assets/stats_{clean_name}.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    return f"assets/stats_{clean_name}.svg"


def generate_hero_banner(
    team: list[str],
    day_number: int,
    weather: str,
    power_pct: float,
    date_label: str,
    handle: str = "github.com/Arudchayan",
    role_line: str = "ML research engineering · evals · reinforcement learning · reproducible systems",
) -> str:
    """Generate the profile hero banner. Dark panel, so it reads on light and dark themes."""
    width, height = 880, 230
    roster = " · ".join(name.upper() for name in team)
    pct = max(0.0, min(power_pct, 1.0))

    cx, cy, radius = 790, 112, 52
    circumference = 2 * math.pi * radius

    svg = f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Arudchayan BattleOps Command Center banner">
  <title>Arudchayan · BattleOps Command Center</title>
  <defs>
    <linearGradient id="hero-bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0B0817"/>
      <stop offset="0.55" stop-color="#120D26"/>
      <stop offset="1" stop-color="#0A1224"/>
    </linearGradient>
    <radialGradient id="hero-glow" cx="0.82" cy="0.15" r="0.7">
      <stop offset="0" stop-color="#7C3AED" stop-opacity="0.35"/>
      <stop offset="1" stop-color="#7C3AED" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="hero-teal" cx="0.1" cy="1" r="0.8">
      <stop offset="0" stop-color="#06B6D4" stop-opacity="0.18"/>
      <stop offset="1" stop-color="#06B6D4" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="hero-accent" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#8B5CF6"/>
      <stop offset="0.5" stop-color="#22D3EE"/>
      <stop offset="1" stop-color="#F472B6"/>
    </linearGradient>
    <pattern id="hero-grid" width="32" height="32" patternUnits="userSpaceOnUse">
      <path d="M32 0H0V32" fill="none" stroke="#FFFFFF" stroke-opacity="0.035"/>
    </pattern>
  </defs>
  <rect width="{width}" height="{height}" rx="20" fill="url(#hero-bg)"/>
  <rect width="{width}" height="{height}" rx="20" fill="url(#hero-grid)"/>
  <rect width="{width}" height="{height}" rx="20" fill="url(#hero-glow)"/>
  <rect width="{width}" height="{height}" rx="20" fill="url(#hero-teal)"/>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="20" fill="none" stroke="#FFFFFF" stroke-opacity="0.10"/>
  <rect x="24" y="26" width="4" height="178" rx="2" fill="url(#hero-accent)"/>

  <text x="46" y="48" font-family="{MONO}" font-size="10" letter-spacing="3.4" fill="#8B5CF6">BATTLEOPS // COMMAND CENTER</text>
  <text x="44" y="106" font-family="{MONO}" font-size="46" font-weight="800" letter-spacing="-1" fill="#F8F7FF">ARUDCHAYAN</text>
  <text x="46" y="138" font-family="{MONO}" font-size="12.5" letter-spacing="0.4" fill="#C9C4E0">{html.escape(role_line)}</text>
  <text x="46" y="166" font-family="{MONO}" font-size="9.5" letter-spacing="1.6" fill="#6F6A88">ACTIVE ROSTER</text>
  <text x="46" y="188" font-family="{MONO}" font-size="10.5" letter-spacing="1" fill="#A79FC4">{html.escape(roster)}</text>

  <g transform="translate({cx},{cy})">
    <circle r="{radius}" fill="#0A0817" fill-opacity="0.6" stroke="#FFFFFF" stroke-opacity="0.08" stroke-width="7"/>
    <circle r="{radius}" fill="none" stroke="url(#hero-accent)" stroke-width="7" stroke-linecap="round"
            stroke-dasharray="{circumference * pct:.1f} {circumference:.1f}" transform="rotate(-90)"/>
    <text y="-2" text-anchor="middle" font-family="{MONO}" font-size="7.5" letter-spacing="1.4" fill="#6F6A88">POWER</text>
    <text y="19" text-anchor="middle" font-family="{MONO}" font-size="21" font-weight="800" fill="#F8F7FF">{pct * 100:.1f}<tspan font-size="9" fill="#8B87A8">%</tspan></text>
  </g>

  <g transform="translate(46,208)">
    <circle cx="4" cy="-3" r="3" fill="#22D3EE"/>
    <text x="14" y="0" font-family="{MONO}" font-size="8.5" letter-spacing="1.2" fill="#6F6A88">DAY {day_number} · {html.escape(weather.upper())} · {html.escape(date_label)} · {html.escape(handle.upper())}</text>
  </g>
</svg>"""

    os.makedirs("assets", exist_ok=True)
    with open("assets/hero.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    return "assets/hero.svg"
