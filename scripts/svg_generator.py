from __future__ import annotations

import base64
import datetime
import html
import math
import os
import urllib.request
from collections import defaultdict


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


PIXEL_FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01110"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "01010", "00100", "00100", "00100", "01010", "10001"),
    "Y": ("10001", "01010", "00100", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ".": ("00000", "00000", "00000", "00000", "00000", "00110", "00110"),
    "%": ("11001", "11010", "00100", "00100", "01000", "01011", "10011"),
}

POKEBALL_PATTERN = (
    "..RRRRRR..",
    ".RRRRRRRR.",
    "RRRRRRRRRR",
    "RRRRRRRRRR",
    "RRRRRRRRRR",
    "BBBBBBBBBB",
    "...WWWW...",
    "..WWWWWW..",
    ".WWWWWWWW.",
    "WWWWWWWWWW",
)

WEATHER_PATTERNS = {
    "sun": (
        ("....Y.....", "....Y.....", "..YYYYY...", ".YYYYYYY..", "YYYYYYYYYY",
         ".YYYYYYY..", "..YYYYY...", "....Y.....", "....Y.....", ".........."),
        {"Y": "#F8D030"},
    ),
    "rain": (
        ("...CCC....", "..CCCCC...", ".CCCCCCC..", "CCCCCCCCC.", "..........",
         "..D...D...", ".D...D....", "..D...D...", ".D...D....", ".........."),
        {"C": "#A79FC4", "D": "#22D3EE"},
    ),
    "snow": (
        ("....S.....", ".S..S..S..", "..S.S.S...", "...SSS....", "SSSSSSSSS.",
         "...SSS....", "..S.S.S...", ".S..S..S..", "....S.....", ".........."),
        {"S": "#98D8D8"},
    ),
    "sand": (
        ("..........", "..TTTT....", ".TTTTTT...", "TT..TTTTT.", "...TTTT...",
         "..TTTTTT..", ".TTTT..TT.", "..TTTT....", "..........", ".........."),
        {"T": "#E0C068"},
    ),
}


def _pixel_text(text: str, x: float, y: float, scale: int, color: str) -> str:
    parts = []
    cursor = x
    for char in text.upper():
        if char == " ":
            cursor += 4 * scale
            continue
        glyph = PIXEL_FONT.get(char)
        if not glyph:
            cursor += 6 * scale
            continue
        for row, bits in enumerate(glyph):
            for col, bit in enumerate(bits):
                if bit == "1":
                    parts.append(
                        f"M{cursor + col * scale} {y + row * scale}h{scale}v{scale}h-{scale}z"
                    )
        cursor += 6 * scale
    return f'<path d="{"".join(parts)}" fill="{color}"/>' if parts else ""


def _pixel_width(text: str, scale: int) -> float:
    return sum((4 if char == " " else 6) * scale for char in text.upper()) - scale


def _pixel_icon(pattern: tuple[str, ...], x: float, y: float, scale: int, palette: dict[str, str]) -> str:
    by_color: dict[str, list[str]] = defaultdict(list)
    for row, line in enumerate(pattern):
        for col, char in enumerate(line):
            color = palette.get(char)
            if color:
                by_color[color].append(
                    f"M{x + col * scale} {y + row * scale}h{scale}v{scale}h-{scale}z"
                )
    return "".join(
        f'<path d="{"".join(rects)}" fill="{color}"/>' for color, rects in by_color.items()
    )


_SPRITE_CACHE: dict[str, str | None] = {}


def _embed_sprite(url: str | None) -> str | None:
    if not url:
        return None
    if url in _SPRITE_CACHE:
        return _SPRITE_CACHE[url]
    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "Arudchayan-Trainer-Profile/1.0", "Accept": "image/*"},
        )
        with urllib.request.urlopen(request, timeout=15) as response:
            data = response.read()
        if not data or len(data) > 250_000:
            data_uri = None
        elif data.startswith(b"\x89PNG"):
            data_uri = "data:image/png;base64," + base64.b64encode(data).decode("ascii")
        elif data.startswith(b"GIF8"):
            data_uri = "data:image/gif;base64," + base64.b64encode(data).decode("ascii")
        else:
            data_uri = None
    except Exception:
        data_uri = None
    _SPRITE_CACHE[url] = data_uri
    return data_uri


def generate_hero_banner(
    team: list[str],
    day_number: int,
    weather: str,
    power_pct: float,
    date_label: str,
    sprites: list[str | None] | None = None,
    types: list[list[str]] | None = None,
    archetype: str = "",
    lead: str = "",
    handle: str = "github.com/Arudchayan",
    role_line: str = "ML research engineering · evals · reinforcement learning · reproducible systems",
) -> str:
    """Generate the pixel-art trainer-card banner, with embedded team sprites."""
    width, height = 880, 320
    pct = max(0.0, min(power_pct, 1.0))
    team = team[:6]
    sprites = sprites or []
    types = types or []

    ink = "#0D1220"
    cream = "#F6F1E3"
    gold = "#F8D030"
    cyan = "#22D3EE"
    red = "#E3350D"
    muted = "#6F7A99"
    line = "#26314D"
    lavender = "#A79FC4"

    weather_key = weather.lower()
    if "rain" in weather_key:
        icon_key = "rain"
    elif "snow" in weather_key:
        icon_key = "snow"
    elif "sand" in weather_key:
        icon_key = "sand"
    else:
        icon_key = "sun"
    weather_pattern, weather_palette = WEATHER_PATTERNS[icon_key]

    # Team slots: six party frames across the right side of the card.
    slot_x, slot_y, slot_size, slot_gap = 300, 54, 82, 8
    slots = []
    for index, name in enumerate(team):
        x = slot_x + index * (slot_size + slot_gap)
        is_lead = index == 0
        border = gold if is_lead else line
        slots.append(
            f'<rect x="{x}" y="{slot_y}" width="{slot_size}" height="{slot_size}" '
            f'fill="#0A0F1C" stroke="{border}" stroke-width="2"/>'
        )
        data_uri = _embed_sprite(sprites[index] if index < len(sprites) else None)
        if data_uri:
            slots.append(
                f'<image x="{x + 9}" y="{slot_y + 5}" width="64" height="64" '
                f'href="{data_uri}" xlink:href="{data_uri}" image-rendering="pixelated"/>'
            )
        else:
            slots.append(_pixel_icon(POKEBALL_PATTERN, x + 31, slot_y + 26, 2, {"R": red, "B": "#111827", "W": cream}))

        slot_types = types[index] if index < len(types) else []
        strip_y = slot_y + slot_size - 6
        if slot_types:
            primary = TYPE_COLORS.get(slot_types[0], "#8B5CF6")
            if len(slot_types) > 1:
                secondary = TYPE_COLORS.get(slot_types[1], primary)
                half = slot_size / 2
                slots.append(f'<rect x="{x + 2}" y="{strip_y}" width="{half - 2}" height="4" fill="{primary}"/>')
                slots.append(f'<rect x="{x + half}" y="{strip_y}" width="{half - 2}" height="4" fill="{secondary}"/>')
            else:
                slots.append(f'<rect x="{x + 2}" y="{strip_y}" width="{slot_size - 4}" height="4" fill="{primary}"/>')
        slots.append(_pixel_text(f"{index + 1:02d}", x + 5, slot_y + slot_size - 16, 1, gold if is_lead else muted))

    power_segments = 10
    filled_segments = round(pct * power_segments)
    bar_x, bar_y, seg_w, seg_h, seg_gap = 600, 194, 20, 14, 3
    power_bar = []
    for segment in range(power_segments):
        x = bar_x + segment * (seg_w + seg_gap)
        fill = "#4ADE80" if segment < filled_segments else "#1B2438"
        power_bar.append(
            f'<rect x="{x}" y="{bar_y}" width="{seg_w}" height="{seg_h}" fill="{fill}" stroke="#070A12" stroke-width="2"/>'
        )

    id_label = f"ID No. {day_number}"
    svg = f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" role="img" aria-label="Arudchayan pixel trainer card">
  <title>Arudchayan · BattleOps trainer card</title>
  <defs>
    <pattern id="px-grid" width="16" height="16" patternUnits="userSpaceOnUse">
      <rect width="8" height="8" fill="#FFFFFF" fill-opacity="0.022"/>
      <rect x="8" y="8" width="8" height="8" fill="#FFFFFF" fill-opacity="0.022"/>
    </pattern>
  </defs>

  <rect width="{width}" height="{height}" fill="{cream}"/>
  <rect x="4" y="4" width="{width - 8}" height="{height - 8}" fill="{ink}"/>
  <rect x="4" y="4" width="{width - 8}" height="{height - 8}" fill="url(#px-grid)"/>
  <rect x="4" y="4" width="{width - 8}" height="10" fill="{red}"/>
  <rect x="4" y="14" width="{width - 8}" height="2" fill="#8E1F0A"/>

  {_pixel_icon(POKEBALL_PATTERN, 26, 28, 2, {"R": red, "B": "#111827", "W": cream})}
  {_pixel_text("TRAINER CARD", 54, 32, 2, cream)}
  {_pixel_text(id_label, width - 26 - _pixel_width(id_label, 2), 32, 2, muted)}

  {_pixel_text("ARUDCHAYAN", 26, 66, 4, cream)}
  {_pixel_text("ML RESEARCH ENGINEER", 28, 106, 2, gold)}
  <text x="28" y="126" font-family="{MONO}" font-size="9.5" letter-spacing="0.6" fill="{lavender}">EVALS · RL · REPRODUCIBLE SYSTEMS</text>
  {_pixel_text(f"LEAD // {lead.upper()}", 28, 142, 1, cyan)}

  {''.join(slots)}

  <rect x="26" y="154" width="{width - 52}" height="2" fill="{line}"/>
  <rect x="26" y="154" width="34" height="2" fill="{red}"/>

  {_pixel_text(archetype.upper(), 26, 172, 2, cream)}
  {_pixel_icon(weather_pattern, 26, 198, 2, weather_palette)}
  {_pixel_text(weather.upper(), 52, 202, 2, gold)}
  <text x="26" y="246" font-family="{MONO}" font-size="9" letter-spacing="0.8" fill="{muted}">{html.escape(date_label)} · {html.escape(handle.upper())}</text>

  {_pixel_text("POWER", 600, 172, 2, cream)}
  {''.join(power_bar)}
  {_pixel_text(f"{pct * 100:.1f}%", 600, 220, 2, cream)}
  <rect x="708" y="226" width="6" height="6" fill="#4ADE80"/>
  {_pixel_text("ONLINE", 720, 225, 1, "#4ADE80")}
  <text x="600" y="252" font-family="{MONO}" font-size="8.5" letter-spacing="0.8" fill="{muted}">EVERY 24H · GITHUB ACTIONS</text>
</svg>"""

    os.makedirs("assets", exist_ok=True)
    with open("assets/hero.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    return "assets/hero.svg"


# ---------------------------------------------------------------------------
# Editorial field-guide hero (final direction)
# ---------------------------------------------------------------------------

PAPER = "#F2EBD9"
PAPER_LIGHT = "#FAF5E6"
INK = "#26221B"
SOFT_INK = "#463E32"
SAGE = "#7C8C6D"
SAGE_DARK = "#58684E"
FIELD_RED = "#B23A2B"
FIELD_RED_DARK = "#7C2418"
FIELD_RULE = "#D5C8B0"
SERIF = "Georgia,'Iowan Old Style','Palatino Linotype','Times New Roman',serif"
FIELD_MONO = "'Courier New',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"


def _field_text(x, y, value, *, size=9, fill=INK, family=FIELD_MONO, weight="normal",
                style="normal", anchor="start", tracking=0, opacity=1.0):
    return (
        f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
        f'font-weight="{weight}" font-style="{style}" text-anchor="{anchor}" '
        f'letter-spacing="{tracking}" fill="{fill}" opacity="{opacity}">'
        f'{html.escape(str(value))}</text>'
    )


def _field_rule(x1, y1, x2, y2, color=FIELD_RULE, width=1.0, opacity=1.0):
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
        f'stroke-width="{width}" opacity="{opacity}"/>'
    )


def _corner_mounts(x, y, w, h, size=17, color=SAGE):
    return "".join([
        f'<path d="M{x} {y}h{size}l-{size} {size}z" fill="{color}" opacity="0.9"/>',
        f'<path d="M{x + w} {y}h-{size}l{size} {size}z" fill="{color}" opacity="0.9"/>',
        f'<path d="M{x} {y + h}h{size}l-{size} -{size}z" fill="{color}" opacity="0.9"/>',
        f'<path d="M{x + w} {y + h}h-{size}l{size} -{size}z" fill="{color}" opacity="0.9"/>',
    ])


def _dex_from_sprite(url: str | None) -> str:
    if not url:
        return "???"
    tail = url.rsplit("/", 1)[-1]
    number = tail.split(".")[0]
    return number.zfill(3) if number.isdigit() else "???"


def _split_arrow_value(x, y, value, size=20):
    """Draw a value containing an arrow without relying on font glyph coverage."""
    if "\u2192" not in value:
        return _field_text(x, y, value, size=size, family=SERIF, fill=INK)
    left, right = [part.strip() for part in value.split("\u2192", 1)]
    left_width = max(30, len(left) * size * 0.52)
    parts = [_field_text(x, y, left, size=size, family=SERIF, fill=INK)]
    arrow_x = x + left_width + 5
    parts.append(
        f'<path d="M{arrow_x:.1f} {y - 4:.1f}h13m-4 -4l4 4-4 4" fill="none" '
        f'stroke="{FIELD_RED}" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>'
    )
    parts.append(_field_text(arrow_x + 23, y, right, size=size, family=SERIF, fill=INK))
    return "".join(parts)


def _format_field_date(date_label: str) -> str:
    try:
        parsed = datetime.datetime.strptime(date_label, "%Y-%m-%d")
        return parsed.strftime("%d %b %Y").upper()
    except ValueError:
        return date_label


def generate_field_guide_hero(
    team: list[str],
    day_number: int,
    weather: str,
    power_pct: float,
    date_label: str,
    sprites: list[str | None] | None = None,
    types: list[list[str]] | None = None,
    archetype: str = "",
    lead: str = "",
    proofs: list[dict] | None = None,
    handle: str = "github.com/Arudchayan",
) -> str:
    """Render the profile hero as a pinned field-guide plate.

    Real text for everything load-bearing, embedded sprites, no theme queries.
    """
    width, height = 880, 320
    team = team[:6]
    sprites = sprites or []
    types = types or []
    proofs = (proofs or [])[:3]
    pct = max(0.0, min(power_pct, 1.0))
    date_text = _format_field_date(date_label)
    lead = lead or (team[0] if team else "Arudchayan")
    lead_types = types[0] if types else []
    lead_type_text = " / ".join(t.upper() for t in lead_types) or "UNKNOWN"

    lead_sprite = sprites[0] if sprites else None
    lead_uri = _embed_sprite(lead_sprite)
    if lead_uri:
        lead_image = (
            f'<image x="650" y="90" width="96" height="96" href="{lead_uri}" '
            f'xlink:href="{lead_uri}" image-rendering="pixelated"/>'
        )
    else:
        lead_image = _pixel_icon(POKEBALL_PATTERN, 674, 114, 2, {"R": FIELD_RED, "B": INK, "W": PAPER_LIGHT})

    # Evidence ledger: value, method label, project + status.
    evidence = []
    column_x = [30, 190, 350]
    for index, proof in enumerate(proofs[:3]):
        x = column_x[index]
        label = f"{proof.get('source', '')} · {proof.get('label', '')}".strip(" ·")
        evidence.append(_field_text(x, 232, label, size=7.0, tracking=0.3, fill=SAGE_DARK))
        evidence.append(_split_arrow_value(x, 250, str(proof.get("value", "")), size=20))
        status = str(proof.get("status", "")).upper()
        status_color = SAGE_DARK if status == "PUBLIC" else FIELD_RED
        evidence.append(_field_text(x, 260, status, size=6.0, tracking=1.0, fill=status_color))
    if not evidence:
        evidence.append(_field_text(30, 240, "Evidence ledger pending.", size=11, family=SERIF, fill=SOFT_INK))

    # Paratype plate: up to five reserve specimens, centred if fewer.
    paratypes = []
    reserve = list(zip(team[1:6], sprites[1:6], types[1:6]))
    if reserve:
        spacing = 50
        total = spacing * (len(reserve) - 1)
        start = 698 - total / 2
        for index, (name, sprite, _) in enumerate(reserve):
            center = start + index * spacing
            uri = _embed_sprite(sprite)
            if uri:
                paratypes.append(
                    f'<image x="{center - 15:.1f}" y="250" width="30" height="30" '
                    f'href="{uri}" xlink:href="{uri}" image-rendering="pixelated"/>'
                )
            else:
                paratypes.append(
                    _pixel_icon(POKEBALL_PATTERN, center - 9, 256, 1, {"R": FIELD_RED, "B": INK, "W": PAPER_LIGHT})
                )
            paratypes.append(
                _field_text(center, 291, f"No. {_dex_from_sprite(sprite)}", size=6.2,
                            tracking=0.4, fill=SOFT_INK, anchor="middle", opacity=0.82)
            )

    svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" role="img" aria-label="Arudchayan, ML research engineer. Evaluation evidence and a pinned {html.escape(lead)} specimen.">
  <title>Arudchayan · ML research engineer — evaluation is field work</title>
  <desc>Evaluation evidence: {html.escape("; ".join(str(p.get("value", "")) + " " + str(p.get("label", "")) for p in proofs))}. Open to research engineering roles.</desc>
  <defs>
    <pattern id="field-dotgrid" width="16" height="16" patternUnits="userSpaceOnUse">
      <circle cx="8" cy="8" r="0.55" fill="{INK}" opacity="0.055"/>
    </pattern>
    <filter id="field-card-shadow" x="-10%" y="-10%" width="120%" height="125%">
      <feDropShadow dx="0" dy="2.5" stdDeviation="3" flood-color="#4A3A24" flood-opacity="0.14"/>
    </filter>
  </defs>

  <rect width="{width}" height="{height}" fill="{PAPER}"/>
  <rect width="{width}" height="{height}" fill="url(#field-dotgrid)"/>

  <g filter="url(#field-card-shadow)">
    <rect x="548" y="42" width="300" height="250" fill="{PAPER_LIGHT}" stroke="#CBBDA3" stroke-width="1"/>
  </g>
  <rect x="549" y="43" width="298" height="248" fill="none" stroke="{PAPER}" stroke-width="1"/>

  <rect x="30" y="50" width="21" height="2.6" fill="{FIELD_RED}"/>
  {_field_text(58, 57.5, "ARUDCHAYAN", size=10, weight="bold", tracking=2.0, fill=INK)}
  {_field_text(178, 57.5, "· ML RESEARCH ENGINEER", size=10, tracking=1.8, fill=SAGE_DARK)}

  <text x="30" y="103" font-family="{SERIF}" font-size="37" fill="{INK}" letter-spacing="-0.7">Evals that check</text>
  <text x="30" y="141" font-family="{SERIF}" font-size="37" fill="{INK}" letter-spacing="-0.7">whether the check works.</text>

  {_field_text(30, 166, "ABSTRACT", size=6.8, tracking=2.4, fill=FIELD_RED)}
  <text x="30" y="183" font-family="{SERIF}" font-size="11.4" fill="{SOFT_INK}">Evaluation harnesses for small models: monitorability, agent-safety gates,</text>
  <text x="30" y="198" font-family="{SERIF}" font-size="11.4" fill="{SOFT_INK}">and reproducible systems.</text>

  {_field_rule(30, 208, 520, 208, FIELD_RULE, 0.9)}
  {_field_rule(30, 208, 46, 208, FIELD_RED, 1.6)}
  {_field_text(30, 221, "EVIDENCE", size=6.8, tracking=1.6, fill=FIELD_RED)}
  {''.join(evidence)}

  {_field_rule(30, 266, 520, 266, FIELD_RULE, 0.9)}
  {_field_text(30, 282, f"SEED {day_number} · {weather.upper()} · {pct * 100:.1f}% POWER", size=8.2, tracking=1.1, fill=SAGE_DARK)}

  {_field_text(562, 60, "SPECIMEN PLATE", size=6.8, tracking=2.2, fill=SAGE_DARK)}
  {_field_text(834, 60, f"No. {_dex_from_sprite(lead_sprite)}", size=6.8, tracking=1.4, fill=INK, anchor="end")}
  {_field_rule(562, 66, 834, 66, FIELD_RULE, 0.8)}

  <circle cx="698" cy="138" r="54" fill="{SAGE}" opacity="0.10"/>
  {_corner_mounts(634, 74, 128, 128, 17)}
  {lead_image}
  <g transform="rotate(-10 763 93)">
    <ellipse cx="763" cy="93" rx="23" ry="10" fill="none" stroke="{FIELD_RED}" stroke-width="1.4" opacity="0.9"/>
    <ellipse cx="763" cy="93" rx="19.5" ry="7.2" fill="none" stroke="{FIELD_RED}" stroke-width="0.5" opacity="0.55"/>
    <text x="763" y="95.6" text-anchor="middle" font-family="{FIELD_MONO}" font-size="7.2" font-weight="bold" letter-spacing="1.2" fill="{FIELD_RED}">LEAD</text>
  </g>
  {_field_text(698, 222, lead.upper(), size=15, family=SERIF, tracking=3.2, fill=INK, anchor="middle")}
  {_field_text(698, 234, f"{lead_type_text} · LEAD SPECIMEN", size=6.4, tracking=1.5, fill=SAGE_DARK, anchor="middle")}
  {_field_rule(562, 242, 834, 242, FIELD_RULE, 0.8)}
  {''.join(paratypes)}

  <rect x="0" y="0" width="{width}" height="30" fill="{FIELD_RED}"/>
  <rect x="0" y="29" width="{width}" height="1" fill="{FIELD_RED_DARK}"/>
  <circle cx="27" cy="15" r="5.6" fill="none" stroke="{PAPER_LIGHT}" stroke-width="1.1"/>
  <path d="M21.4 15h11.2" stroke="{PAPER_LIGHT}" stroke-width="1.1"/>
  <circle cx="27" cy="15" r="1.9" fill="{PAPER_LIGHT}"/>
  {_field_text(42, 18.3, "POKÉDEX FIELD GUIDE", size=8.6, tracking=2.7, fill=PAPER_LIGHT)}
  <rect x="345" y="7" width="190" height="16" fill="none" stroke="{PAPER_LIGHT}" stroke-width="0.8" opacity="0.65"/>
  {_field_text(440, 18.2, "OPEN TO RESEARCH ROLES", size=7.2, tracking=1.7, fill=PAPER_LIGHT, anchor="middle")}
  {_field_text(848, 18, date_text, size=7.5, tracking=1.6, fill=PAPER_LIGHT, anchor="end", opacity="0.92")}

  {_field_rule(30, 302, 848, 302, FIELD_RULE, 0.9)}
  {_field_text(30, 315, handle, size=7.4, tracking=1.0, fill=INK, opacity=0.85)}
  {_field_text(440, 315, "EVALS · AGENT SAFETY · REPRODUCIBLE SYSTEMS", size=7.6, tracking=1.3, fill=SAGE_DARK, anchor="middle")}
  {_field_text(848, 315, "p. 01", size=7.4, tracking=1.0, fill=SAGE_DARK, anchor="end")}

  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" fill="none" stroke="{INK}" stroke-width="1" opacity="0.85"/>
</svg>'''

    os.makedirs("assets", exist_ok=True)
    with open("assets/hero.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    return "assets/hero.svg"
