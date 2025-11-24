import math
import os

def normalize_name(name: str) -> str:
    return name.lower().strip().replace(" ", "-").replace(".", "").replace("'", "")

def generate_radar_chart(stats: dict, pokemon_name: str) -> str:
    """Generate a simple SVG radar chart for stats."""
    labels = ['HP', 'Atk', 'Def', 'Spe', 'SpD', 'SpA']
    keys = ['hp', 'attack', 'defense', 'speed', 'special-defense', 'special-attack']
    values = [stats.get(k, 0) for k in keys]
    max_val = 255

    # SVG Config
    size = 200
    center = size // 2
    radius = 80

    # Calculate points
    points = []
    angle_step = (2 * math.pi) / 6

    for i, val in enumerate(values):
        angle = i * angle_step - (math.pi / 2) # Start at top
        r = (val / max_val) * radius
        x = center + r * math.cos(angle)
        y = center + r * math.sin(angle)
        points.append(f"{x},{y}")

    points_str = " ".join(points)

    # Background Hexagon
    bg_points = []
    for i in range(6):
        angle = i * angle_step - (math.pi / 2)
        x = center + radius * math.cos(angle)
        y = center + radius * math.sin(angle)
        bg_points.append(f"{x},{y}")
    bg_str = " ".join(bg_points)

    svg = f"""<svg width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg">
      <polygon points="{bg_str}" fill="rgba(255,255,255,0.1)" stroke="#444" stroke-width="1"/>
      <polygon points="{points_str}" fill="rgba(106, 13, 173, 0.5)" stroke="#6A0DAD" stroke-width="2"/>
      <circle cx="{center}" cy="{center}" r="2" fill="#fff"/>
    </svg>"""

    clean_name = normalize_name(pokemon_name)
    filename = f"assets/stats_{clean_name}.svg"

    # Ensure assets directory exists (though build script usually creates it)
    if not os.path.exists("assets"):
        os.makedirs("assets")

    with open(filename, "w") as f:
        f.write(svg)

    return filename
