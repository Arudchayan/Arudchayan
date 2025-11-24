import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import urllib.request
from io import BytesIO

def generate_team_banner(pokemon_list: list, weather_type: str) -> str:
    """
    Generates a composite image of the team on a background.
    """
    # Canvas settings
    width = 800
    height = 400

    # Background colors based on weather
    weather_colors = {
        "Clear Skies": "#87CEEB", # Sky Blue
        "Harsh Sunlight": "#FFD700", # Gold
        "Rain": "#4682B4", # Steel Blue
        "Sandstorm": "#F4A460", # Sandy Brown
        "Snow": "#E0FFFF", # Light Cyan
    }

    bg_color = weather_colors.get(weather_type, "#2C3E50") # Default Dark Blue

    # Create base image
    base = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(base)

    # Draw simple terrain (green floor)
    draw.rectangle([(0, height - 100), (width, height)], fill="#228B22")

    # Load and paste sprites
    # We arrange them in a V formation
    positions = [
        (350, 150), # Lead (Center)
        (200, 180), (500, 180),
        (100, 220), (600, 220),
        (50, 250)
    ]

    for i, p_data in enumerate(pokemon_list[:6]):
        if i >= len(positions): break

        sprite_url = p_data.get('sprite')
        if not sprite_url: continue

        try:
            # Download sprite
            with urllib.request.urlopen(sprite_url) as url:
                img_data = url.read()

            sprite = Image.open(BytesIO(img_data)).convert("RGBA")

            # Resize (Gen 5 sprites are small, scale up 2x)
            sprite = sprite.resize((sprite.width * 2, sprite.height * 2), Image.Resampling.NEAREST)

            # Paste with transparency
            x, y = positions[i]

            # Adjust y to align bottom
            y = y - sprite.height // 2

            base.paste(sprite, (x, y), sprite)

        except Exception as e:
            print(f"Failed to load sprite for {p_data['name']}: {e}")

    # Add overlay effect for weather
    if weather_type == "Rain":
        overlay = Image.new('RGBA', (width, height), (0, 0, 50, 50))
        base.paste(overlay, (0,0), overlay)
    elif weather_type == "Harsh Sunlight":
        overlay = Image.new('RGBA', (width, height), (255, 255, 0, 30))
        base.paste(overlay, (0,0), overlay)

    # Save
    if not os.path.exists("assets"):
        os.makedirs("assets")

    filename = "assets/team_banner.png"
    base.save(filename)
    return filename
