import math
import os

def generate_radar_chart(stats: dict, clean_name: str) -> str:
    """Generate a simple SVG radar chart for stats."""
    keys = ['hp', 'attack', 'defense', 'speed', 'special-defense', 'special-attack']
    values = [stats.get(k, 0) for k in keys]
    max_val = 255

    # SVG Config
    size = 200
    center = size // 2
    radius = 80

    # Calculate points
    angle_step = (2 * math.pi) / 6

    def ring(multipliers) -> str:
        return " ".join(
            f"{center + m * radius * math.cos(i * angle_step - math.pi / 2)},"
            f"{center + m * radius * math.sin(i * angle_step - math.pi / 2)}"
            for i, m in enumerate(multipliers)
        )

    points_str = ring(v / max_val for v in values)
    bg_str = ring([1] * 6)

    svg = f"""<svg width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg">
      <polygon points="{bg_str}" fill="rgba(255,255,255,0.1)" stroke="#444" stroke-width="1"/>
      <polygon points="{points_str}" fill="rgba(106, 13, 173, 0.5)" stroke="#6A0DAD" stroke-width="2"/>
      <circle cx="{center}" cy="{center}" r="2" fill="#fff"/>
    </svg>"""

    os.makedirs("assets", exist_ok=True)

    with open(f"assets/stats_{clean_name}.svg", "w") as f:
        f.write(svg)
