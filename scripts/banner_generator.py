import os
from PIL import Image, ImageDraw, ImageOps
import urllib.request
from io import BytesIO

def download_image(url):
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return Image.open(BytesIO(response.read()))
    except Exception as e:
        print(f"Failed to download image from {url}: {e}")
        return None

def generate_team_banner(pokemon_sprites, weather_type="Clear Skies"):
    """
    Generates a composite team banner.
    pokemon_sprites: List of URLs or Image objects.
    weather_type: String determining background color/style.
    """

    # Canvas Settings
    width = 800
    height = 300
    banner = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(banner)

    # 1. Background Generation
    weather_colors = {
        "Clear Skies": [(135, 206, 235), (255, 255, 255)], # Sky Blue
        "Harsh Sunlight": [(255, 165, 0), (255, 69, 0)], # Orange/Red
        "Rain": [(25, 25, 112), (100, 149, 237)], # Dark Blue
        "Sandstorm": [(210, 180, 140), (139, 69, 19)], # Tan/Brown
        "Snow": [(224, 255, 255), (240, 255, 255)], # Light Cyan
    }

    colors = weather_colors.get(weather_type, [(50, 50, 50), (20, 20, 20)])

    # Simple Vertical Gradient
    gradient = Image.linear_gradient("L").resize((width, height))
    banner.paste(ImageOps.colorize(gradient, black=colors[0], white=colors[1]))

    # Add simplified "Ground"
    draw.rectangle([(0, height - 50), (width, height)], fill=(40, 40, 40, 200))

    # 2. Composite Sprites
    # We expect up to 6 sprites. We distribute them across the width.
    num_sprites = len(pokemon_sprites)
    if num_sprites > 0:
        spacing = width // (num_sprites + 1)

        for i, sprite_url in enumerate(pokemon_sprites):
            if not sprite_url:
                continue

            sprite = download_image(sprite_url)
            if not sprite:
                continue

            # Resize if necessary (standardize to ~120px)
            base_size = 150
            sprite = sprite.convert("RGBA")
            sprite.thumbnail((base_size, base_size), Image.Resampling.LANCZOS)

            # Position: Centered horizontally in its slot, bottom aligned to "ground"
            x_pos = (i + 1) * spacing - (sprite.width // 2)
            y_pos = height - 50 - sprite.height + 10 # Slight overlap with ground

            banner.alpha_composite(sprite, dest=(x_pos, y_pos))

    # 3. Save
    output_dir = "assets"
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "team_banner.png")
    banner.save(output_path)
    print(f"Banner saved to {output_path}")

