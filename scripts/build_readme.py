#!/usr/bin/env python3
import json
import os
import datetime
import random
import re
import urllib.request
import urllib.error
import time

ROYAL = "#6A0DAD"

# Pokémon ASCII art library (simple versions)
POKEMON_ASCII_ART = {
    "pikachu": """
    (\\__/)
    (o^.^)
    z(_(")(")
    """,
    "charizard": """
      /\\___/\\
     ( o   o )
     (  =^=  )
      ) ~ ~ (
     /|     |\\
    (_|     |_)
    """,
    "mewtwo": """
      ___
     /   \\
    | O O |
    |  >  |
    |     |
     \\___/
    /_/ \\_\\
    """,
    "rayquaza": """
    ~~~~~~
   ~~~~~~~
  ~~~~~~~~
 ~~~◉~◉~~~
  ~~~~~~~~
   ~~~~~~~
    ~~~~~~
    """,
    "gengar": """
     /\\_/\\
    ( o.o )
     > ^ <
    /|   |\\
   (_|   |_)
    """,
    "metagross": """
    ╔═══╗
    ║ ◉ ║
    ║◉ ◉║
    ╚═══╝
     ║║║
     ███
    """,
    "decidueye": """
      /\\
     /  \\
    | ◉◉ |
     \\  /
      \\/
     /||\\
    """,
    "noivern": """
     /\\_/\\
    ( O O )
    (  V  )
     |   |
     -----
    """,
    "zeraora": """
      /\\
     /  \\
    | ◉◉ |
    |  < |
     \\ /
     / \\
    """,
    "default": """
      ___
     /   \\
    | O O |
     \\ ^ /
      |||
    """
}

TYPE_EMOJIS = {
    "normal": "⚪", "fire": "🔥", "water": "💧", "electric": "⚡",
    "grass": "🌿", "ice": "🧊", "fighting": "🥊", "poison": "☠️",
    "ground": "🌍", "flying": "🕊️", "psychic": "🔮", "bug": "🐛",
    "rock": "🪨", "ghost": "👻", "dragon": "🐉", "dark": "🌙",
    "steel": "⚙️", "fairy": "✨"
}

def fetch_pokemon_data(pokemon_name):
    """Fetch Pokémon data from PokéAPI"""
    try:
        url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            
        # Get species data for flavor text
        species_url = data['species']['url']
        with urllib.request.urlopen(species_url, timeout=5) as response:
            species_data = json.loads(response.read().decode())
            
        time.sleep(0.5)  # Be nice to the API
        
        # Get sprite URLs - prefer animated!
        sprites = data['sprites']
        sprite_url = None
        
        # Priority order: Gen 5 animated > Showdown animated > Default
        if sprites.get('versions', {}).get('generation-v', {}).get('black-white', {}).get('animated', {}).get('front_default'):
            sprite_url = sprites['versions']['generation-v']['black-white']['animated']['front_default']
        elif sprites.get('other', {}).get('showdown', {}).get('front_default'):
            sprite_url = sprites['other']['showdown']['front_default']
        elif sprites.get('front_default'):
            sprite_url = sprites['front_default']
        
        # Shiny sprite as backup option
        shiny_sprite = sprites.get('front_shiny')
        
        return {
            'name': data['name'].title(),
            'types': [t['type']['name'] for t in data['types']],
            'height': data['height'] / 10,  # Convert to meters
            'weight': data['weight'] / 10,  # Convert to kg
            'stats': {s['stat']['name']: s['base_stat'] for s in data['stats']},
            'abilities': [a['ability']['name'].replace('-', ' ').title() for a in data['abilities']],
            'moves': [m['move']['name'].replace('-', ' ').title() for m in data['moves'][:4]],
            'flavor_text': get_english_flavor_text(species_data),
            'sprite': sprite_url,
            'shiny_sprite': shiny_sprite,
            'id': data['id']
        }
    except Exception as e:
        print(f"Warning: Could not fetch data for {pokemon_name}: {e}")
        return None

def get_english_flavor_text(species_data):
    """Extract English flavor text"""
    for entry in species_data.get('flavor_text_entries', []):
        if entry['language']['name'] == 'en':
            return entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
    return "A mysterious Pokémon that loves to code!"

def create_stat_bar(value, max_value=255):
    """Create a visual stat bar"""
    value = max(value, 0)
    filled = int((value / max_value) * 20)
    filled = max(0, min(20, filled))
    return '[' + '█' * filled + '░' * (20 - filled) + ']'


def create_power_gauge(value, max_value=1530, length=30):
    """Render a larger gauge for whole-team power analytics"""
    value = max(value, 0)
    ratio = min(value / max_value, 1) if max_value else 0
    filled = int(ratio * length)
    filled = max(0, min(length, filled))
    bar = '[' + '█' * filled + '░' * (length - filled) + ']'
    return f"{bar} {ratio * 100:5.1f}% capacity"

def get_pokemon_ascii(name):
    """Get ASCII art for a Pokémon - DEPRECATED, kept for fallback"""
    name_lower = name.lower()
    return POKEMON_ASCII_ART.get(name_lower, POKEMON_ASCII_ART['default'])

def get_pokemon_sprite_html(sprite_url, name, size=150):
    """Generate HTML for Pokémon sprite"""
    if sprite_url:
        return f'<img src="{sprite_url}" alt="{name}" width="{size}" height="{size}"/>'
    else:
        # Fallback to ASCII if no sprite
        ascii_art = get_pokemon_ascii(name)
        return f"```\n{ascii_art}\n```"

def get_type_emoji(type_name):
    """Get emoji for a type"""
    return TYPE_EMOJIS.get(type_name, "⚪")

def pick_index(n):
    """Deterministic by date: different one each day"""
    today = datetime.datetime.now(datetime.UTC).date().toordinal()
    return today % n

root = os.path.dirname(os.path.dirname(__file__))

# Load archetypes
with open(os.path.join(root, "data", "archetypes.json")) as f:
    arc = json.load(f)

idx = pick_index(len(arc))
chosen = arc[idx]

print(f"🎯 Building README for archetype: {chosen['title']}")
print(f"👑 Team Leader: {chosen['lead']}")

# Fetch Pokémon data
print("\n🔍 Fetching Pokémon data from PokéAPI...")
pokemon_data = {}
for pokemon_name in chosen['team']:
    clean_name = pokemon_name.lower().replace('mega ', '')
    print(f"  📡 Fetching {pokemon_name}...")
    data = fetch_pokemon_data(clean_name)
    if data:
        pokemon_data[pokemon_name] = data
    else:
        # Fallback data
        pokemon_data[pokemon_name] = {
            'name': pokemon_name,
            'types': ['normal'],
            'height': 1.0,
            'weight': 10.0,
            'stats': {'hp': 100, 'attack': 100, 'defense': 100, 'special-attack': 100, 'special-defense': 100, 'speed': 100},
            'abilities': ['Unknown'],
            'moves': ['Tackle', 'Quick Attack', 'Hyper Beam', 'Rest'],
            'flavor_text': 'A mysterious Pokémon!',
            'sprite': None,
            'shiny_sprite': None,
            'id': 0
        }

# Pick a random Pokémon for the encounter
random_pokemon_names = ['ditto', 'pikachu', 'eevee', 'snorlax', 'magikarp', 'gyarados', 'dragonite', 'lucario']
random_choice = random.choice(random_pokemon_names)
print(f"\n✨ Random encounter: {random_choice.title()}")
random_pokemon_data = fetch_pokemon_data(random_choice)

# Load template
with open(os.path.join(root, "README.template.md")) as f:
    template = f.read()

# Current date info
current_date = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d %H:%M UTC")
day_number = datetime.datetime.now(datetime.UTC).date().toordinal()

# Get lead Pokémon data
lead_name = chosen['lead']
lead_data = pokemon_data.get(lead_name, {})

# Prepare lead Pokémon info
lead_types = ' '.join([get_type_emoji(t) + t.upper() for t in lead_data.get('types', ['normal'])])
lead_ability = lead_data.get('abilities', ['Unknown'])[0]
lead_nature = random.choice(['Adamant', 'Modest', 'Jolly', 'Timid', 'Bold', 'Calm', 'Careful', 'Hasty'])
lead_stats = lead_data.get('stats', {})

# Get lead emoji
lead_emoji = get_type_emoji(lead_data.get('types', ['normal'])[0])

# Archetype emoji based on type
archetype_emoji = lead_emoji

# Create stat bars for lead
lead_hp = lead_stats.get('hp', 100)
lead_attack = lead_stats.get('attack', 100)
lead_defense = lead_stats.get('defense', 100)
lead_spatk = lead_stats.get('special-attack', 100)
lead_spdef = lead_stats.get('special-defense', 100)
lead_speed = lead_stats.get('speed', 100)

# Calculate power level
power_level = sum([lead_hp, lead_attack, lead_defense, lead_spatk, lead_spdef, lead_speed])
power_gauge = create_power_gauge(power_level)

# Create team visual
team_visual = "\n".join([f"  [{i+1}] {p}" for i, p in enumerate(chosen['team'])])

# Build archetype section
archetype_section = (
    f"> **Rotation Profile:** {chosen['title']}  \n"
    f"> **Command Lead:** {lead_name}  \n"
    f"> **Roster Online:** {', '.join(chosen['team'])}"
)

# Compute holistic team analytics
team_type_counts = {}
team_dossiers = []
fastest_member = (None, {'stats': {'speed': 0}})
heaviest_member = (None, {'weight': 0})
bst_member = (None, 0)
total_speed = 0

for pokemon_name in chosen['team']:
    pdata = pokemon_data.get(pokemon_name, {})
    stats = pdata.get('stats', {})
    types = pdata.get('types', ['normal'])
    abilities = pdata.get('abilities', ['Unknown'])
    moves = pdata.get('moves', ['Tackle'])[:4]
    sprite_html = get_pokemon_sprite_html(pdata.get('sprite'), pokemon_name, 160)

    for t in types:
        team_type_counts[t] = team_type_counts.get(t, 0) + 1

    speed_value = stats.get('speed', 0)
    if speed_value > fastest_member[1]['stats'].get('speed', 0):
        fastest_member = (pokemon_name, pdata)

    weight_value = pdata.get('weight', 0)
    if weight_value > heaviest_member[1].get('weight', 0):
        heaviest_member = (pokemon_name, pdata)

    bst = sum(stats.values()) if stats else 0
    if bst > bst_member[1]:
        bst_member = (pokemon_name, bst)

    total_speed += speed_value

    top_stat_key = max(stats, key=stats.get) if stats else 'hp'
    top_stat_value = stats.get(top_stat_key, 0)
    top_stat_label = top_stat_key.replace('-', ' ').title()
    move_lines = "\n".join([f"  - {move}" for move in moves]) if moves else "  - (pending scouting)"

    dossier = (
        f"<details open>\n"
        f"<summary>⚔️ <strong>{pokemon_name}</strong> · "
        + " / ".join([get_type_emoji(t) + t.upper() for t in types])
        + "</summary>\n\n"
        f"<div align=\"center\">\n{sprite_html}\n</div>\n\n"
        f"- **Base Stat Total:** {bst}\n"
        f"- **Top Stat:** {top_stat_label} ({top_stat_value})\n"
        f"- **Abilities:** {', '.join(abilities)}\n"
        f"- **Signature Moves:**\n{move_lines}\n"
        f"</details>"
    )
    team_dossiers.append(dossier)

unique_type_count = len(team_type_counts)
average_speed = (total_speed / len(chosen['team'])) if chosen['team'] else 0
fastest_name = fastest_member[0] or 'Unknown'
fastest_speed = fastest_member[1]['stats'].get('speed', 0) if fastest_member[0] else 0
heaviest_name = heaviest_member[0] or 'Unknown'
heaviest_weight = heaviest_member[1].get('weight', 0) if heaviest_member[0] else 0
highest_bst_name = bst_member[0] or 'Unknown'
highest_bst_value = bst_member[1]

coverage_lines = []
for t_name, count in sorted(team_type_counts.items(), key=lambda item: (-item[1], item[0])):
    coverage_lines.append(f"- {get_type_emoji(t_name)} **{t_name.upper()}** ×{count}")
type_coverage_block = "\n".join(coverage_lines) if coverage_lines else "- Coverage telemetry unavailable"

bonkers_taglines = [
    "synthetic battle intel streamed straight from Kanto Mission Control",
    "orchestrated like a championship draft board with neon command prompts",
    "tuned for data maximalists chasing legendary-level dashboards",
    "pulling PokéAPI signals into a holo-briefing worthy of a League HQ"
]
bonkers_tagline = random.choice(bonkers_taglines)

lead_stat_roles = {
    'attack': 'Hyper-Offense Spearhead',
    'special-attack': 'Arcane Artillery Node',
    'defense': 'Fortified Bulwark Unit',
    'special-defense': 'Psi-Shield Anchor',
    'speed': 'Supersonic Initiator'
}
lead_stat_map = {
    'attack': lead_attack,
    'special-attack': lead_spatk,
    'defense': lead_defense,
    'special-defense': lead_spdef,
    'speed': lead_speed
}
lead_dominant_stat = max(lead_stat_map, key=lead_stat_map.get)
lead_role = lead_stat_roles.get(lead_dominant_stat, 'Balanced Command Core')

analytics_blurb = (
    f"{lead_name} fronts a {len(chosen['team'])}-unit strike team spanning {unique_type_count} unique typings "
    f"with an average Speed index of {average_speed:.1f}. Fastest scout: {fastest_name} ({fastest_speed} Speed)."
)

# Replace template placeholders
replacements = {
    '{CURRENT_DATE}': current_date,
    '{DAY_NUMBER}': str(day_number),
    '{POKEDEX_COUNT}': str(len(pokemon_data)),
    '{ARCHETYPE_TITLE}': chosen['title'],
    '{ARCHETYPE_EMOJI}': archetype_emoji,
    '{LEAD_POKEMON}': lead_name,
    '{LEAD_EMOJI}': lead_emoji,
    '{LEAD_ASCII}': get_pokemon_sprite_html(lead_data.get('sprite'), lead_name, 200),
    '{LEAD_TYPES}': lead_types,
    '{LEAD_ABILITY}': lead_ability,
    '{LEAD_NATURE}': lead_nature,
    '{LEAD_HEIGHT}': f"{lead_data.get('height', 1.0):.1f}m",
    '{LEAD_WEIGHT}': f"{lead_data.get('weight', 10.0):.1f}kg",
    '{LEAD_HP}': str(lead_hp),
    '{LEAD_ATK}': str(lead_attack),
    '{LEAD_DEF}': str(lead_defense),
    '{LEAD_SPATK}': str(lead_spatk),
    '{LEAD_SPDEF}': str(lead_spdef),
    '{LEAD_SPEED}': str(lead_speed),
    '{LEAD_HP_BAR}': create_stat_bar(lead_hp),
    '{LEAD_ATK_BAR}': create_stat_bar(lead_attack),
    '{LEAD_DEF_BAR}': create_stat_bar(lead_defense),
    '{LEAD_SPATK_BAR}': create_stat_bar(lead_spatk),
    '{LEAD_SPDEF_BAR}': create_stat_bar(lead_spdef),
    '{LEAD_SPEED_BAR}': create_stat_bar(lead_speed),
    '{LEAD_MOVES}': '\n'.join([f"- **{move}**" for move in lead_data.get('moves', ['Tackle'])[:4]]),
    '{POWER_LEVEL}': str(power_level),
    '{POWER_LEVEL_BAR}': power_gauge,
    '{LEAD_ROLE}': lead_role,
    '{TEAM_VISUAL}': team_visual,
    '{TEAM_LIST}': ', '.join(chosen['team']),
    '{MEGA_INFO}': chosen.get('mega') or '—',
    '{ZMOVE_INFO}': chosen.get('z_move') or '—',
    '{TERA_TYPE}': chosen.get('tera_type') or '—',
    '{MEGA_VISUAL}': '◆' if chosen.get('mega') else '—',
    '{ZMOVE_VISUAL}': '▲' if chosen.get('z_move') else '—',
    '{TERA_VISUAL}': '◇' if chosen.get('tera_type') else '—',
    '{MEGA_STONE_EMOJI}': '💎' if chosen.get('mega') else '',
    '{ZMOVE_EMOJI}': '⚡' if chosen.get('z_move') else '',
    '{TERA_EMOJI}': '✨' if chosen.get('tera_type') else '',
    '{GENERATION}': str(random.randint(1, 9)),
    '{API_CALLS}': str(len(pokemon_data) + 1),
    '{ACHIEVEMENT_DATE}': current_date.split()[0],
    '{UNIQUE_TYPE_COUNT}': str(unique_type_count),
    '{AVERAGE_SPEED}': f"{average_speed:.1f}",
    '{FASTEST_MEMBER}': fastest_name,
    '{FASTEST_SPEED}': str(fastest_speed),
    '{HEAVIEST_MEMBER}': heaviest_name,
    '{HEAVIEST_WEIGHT}': f"{heaviest_weight:.1f}kg",
    '{HIGHEST_BST_MEMBER}': highest_bst_name,
    '{HIGHEST_BST}': str(highest_bst_value),
    '{TEAM_DETAIL_BLOCK}': '\n\n'.join(team_dossiers) if team_dossiers else '- No squad dossiers available.',
    '{TYPE_COVERAGE_BLOCK}': type_coverage_block,
    '{BONKERS_TAGLINE}': bonkers_tagline,
    '{ANALYTICS_BLURB}': analytics_blurb,
}

# Add individual Pokémon data for the team
for i, pokemon_name in enumerate(chosen['team'], 1):
    pdata = pokemon_data.get(pokemon_name, {})
    types_str = ' '.join([get_type_emoji(t) for t in pdata.get('types', ['normal'])])
    
    replacements[f'{{POKEMON_{i}_NAME}}'] = pokemon_name
    replacements[f'{{POKEMON_{i}_TYPES}}'] = types_str
    replacements[f'{{POKEMON_{i}_ASCII}}'] = get_pokemon_sprite_html(pdata.get('sprite'), pokemon_name, 120)

# Random Pokémon encounter
if random_pokemon_data:
    random_types = ' '.join([get_type_emoji(t) + t.upper() for t in random_pokemon_data.get('types', ['normal'])])
    replacements['{RANDOM_POKEMON}'] = random_pokemon_data['name'].upper()
    replacements['{RANDOM_POKEMON_ASCII}'] = get_pokemon_sprite_html(random_pokemon_data.get('sprite'), random_pokemon_data['name'], 150)
    replacements['{RANDOM_POKEMON_TYPES}'] = random_types
    replacements['{RANDOM_POKEMON_HEIGHT}'] = f"{random_pokemon_data['height']:.1f}m"
    replacements['{RANDOM_POKEMON_WEIGHT}'] = f"{random_pokemon_data['weight']:.1f}kg"
    replacements['{RANDOM_POKEMON_ABILITIES}'] = ', '.join(random_pokemon_data['abilities'])
    replacements['{RANDOM_POKEMON_FLAVOR}'] = random_pokemon_data['flavor_text']
else:
    replacements['{RANDOM_POKEMON}'] = 'MISSINGNO'
    replacements['{RANDOM_POKEMON_ASCII}'] = get_pokemon_sprite_html(None, 'missingno', 150)
    replacements['{RANDOM_POKEMON_TYPES}'] = '❓ GLITCH'
    replacements['{RANDOM_POKEMON_HEIGHT}'] = '???'
    replacements['{RANDOM_POKEMON_WEIGHT}'] = '???'
    replacements['{RANDOM_POKEMON_ABILITIES}'] = 'ERROR'
    replacements['{RANDOM_POKEMON_FLAVOR}'] = 'A glitch in the matrix!'

# Apply all replacements
output = template
for key, value in replacements.items():
    output = output.replace(key, str(value))

# Update archetype section
output = re.sub(
    r"<!-- CURRENT_ARCHETYPE_START -->.*?<!-- CURRENT_ARCHETYPE_END -->",
    f"<!-- CURRENT_ARCHETYPE_START -->\n{archetype_section}\n<!-- CURRENT_ARCHETYPE_END -->",
    output,
    flags=re.S
)

# Write output
with open(os.path.join(root, "README.md"), "w") as f:
    f.write(output)

print(f"\n✅ README built successfully!")
print(f"🎯 Archetype: {chosen['title']}")
print(f"👑 Lead: {lead_name}")
print(f"⚡ Power Level: {power_level}")
print(f"🎲 Random Encounter: {replacements.get('{RANDOM_POKEMON}', 'Unknown')}")
print(f"\n💜 GOTTA CODE 'EM ALL! 💜")
