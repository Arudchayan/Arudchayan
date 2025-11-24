import os
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

def download_image(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
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
        "Hail": [(200, 230, 255), (255, 250, 250)],
        "Fog": [(169, 169, 169), (211, 211, 211)]
    }

    colors = weather_colors.get(weather_type, [(50, 50, 50), (20, 20, 20)])

    # Simple Vertical Gradient
    for y in range(height):
        r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * y / height)
        g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * y / height)
        b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * y / height)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

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
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, "team_banner.png")
    banner.save(output_path)
    print(f"Banner saved to {output_path}")
    return output_path

if __name__ == "__main__":
    # Test run
    test_sprites = [
        "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/6.png",
        "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png",
        "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/3.png"
    ]
    generate_team_banner(test_sprites, "Harsh Sunlight")
