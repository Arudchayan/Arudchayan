#!/usr/bin/env python3
import json
import os
import datetime
import random
import re
import urllib.request
import urllib.error
import time
from typing import Optional

ROYAL = "#6A0DAD"

VERSION_PRIORITY = [
    "scarlet-violet",
    "sword-shield",
    "brilliant-diamond-and-shining-pearl",
    "ultra-sun-ultra-moon",
    "sun-moon",
    "omega-ruby-alpha-sapphire",
    "x-y",
    "black-2-white-2",
    "black-white",
]

MOVE_METHOD_PRIORITY = {
    "level-up": 0,
    "tutor": 1,
    "machine": 2,
    "egg": 3,
}

# Competitive move priority - these moves should be heavily favored
COMPETITIVE_PRIORITY_MOVES = {
    # Entry Hazards
    'stealth-rock', 'spikes', 'toxic-spikes', 'sticky-web',
    # Hazard Removal
    'rapid-spin', 'defog',
    # Status Moves
    'will-o-wisp', 'thunder-wave', 'toxic', 'spore', 'sleep-powder',
    # Utility
    'protect', 'detect', 'substitute', 'roost', 'recover', 'synthesis', 'moonlight',
    'u-turn', 'volt-switch', 'flip-turn', 'teleport',
    # Priority
    'aqua-jet', 'mach-punch', 'bullet-punch', 'ice-shard', 'shadow-sneak',
    'accelerock', 'sucker-punch', 'extreme-speed',
    # Setup
    'swords-dance', 'dragon-dance', 'nasty-plot', 'calm-mind', 'bulk-up',
    'quiver-dance', 'shell-smash', 'shift-gear',
    # Signature/Powerful
    'earthquake', 'close-combat', 'flare-blitz', 'hydro-pump', 'ice-beam',
    'thunderbolt', 'psychic', 'shadow-ball', 'dragon-claw', 'dragon-pulse',
    'outrage', 'draco-meteor', 'flamethrower', 'surf', 'scald',
}

# Moves to avoid (competitively terrible)
BAD_MOVES = {
    'constrict', 'lick', 'pound', 'scratch', 'tackle', 'confusion',
    'absorb', 'mega-punch', 'mega-kick', 'sonic-boom', 'dragon-rage',
    'fury-attack', 'comet-punch', 'barrage', 'vice-grip',
}

# Competitive ability preferences (prefer these over others)
COMPETITIVE_ABILITIES = {
    'metagross': ['tough-claws', 'clear-body'],
    'gengar': ['cursed-body', 'levitate'],
    'rayquaza': ['air-lock'],
    'zeraora': ['volt-absorb'],
    'noivern': ['infiltrator', 'frisk'],
    'decidueye': ['long-reach', 'overgrow'],
}

# Competitive nature selection
PHYSICAL_NATURES = ['adamant', 'jolly', 'brave', 'impish', 'careful']
SPECIAL_NATURES = ['modest', 'timid', 'quiet', 'bold', 'calm']
MIXED_NATURES = ['hasty', 'naive', 'lonely', 'mild']

# Competitive items by role
COMPETITIVE_ITEMS = {
    'offensive': ['Choice Band', 'Choice Specs', 'Life Orb', 'Choice Scarf', 'Expert Belt'],
    'defensive': ['Leftovers', 'Heavy-Duty Boots', 'Rocky Helmet', 'Assault Vest'],
    'utility': ['Focus Sash', 'Mental Herb', 'Light Clay', 'Eject Button'],
}

MOVE_CACHE: dict[str, dict] = {}

ROLE_BY_STAT = {
    'attack': 'Hyper-Offense Spearhead',
    'special-attack': 'Arcane Artillery Node',
    'defense': 'Fortified Bulwark Unit',
    'special-defense': 'Psi-Shield Anchor',
    'speed': 'Supersonic Initiator',
}

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

LEGENDARY_ROSTER = [
    "mewtwo",
    "lugia",
    "ho-oh",
    "rayquaza",
    "dialga",
    "palkia",
    "giratina",
    "reshiram",
    "zekrom",
    "xerneas",
    "yveltal",
    "zacian",
    "zamazenta",
    "eternatus",
]

WILD_ROSTER = [
    "ditto",
    "pikachu",
    "eevee",
    "snorlax",
    "magikarp",
    "gyarados",
    "dragonite",
    "lucario",
    "gardevoir",
    "tyranitar",
    "garchomp",
    "dragapult",
    "mienshao",
    "mimikyu",
    "noivern",
    "zeraora",
]

SHINY_TRIGGER_RATE = 1 / 48  # noticeably higher than in-game odds to keep things lively

BRANCH_PATHS = [
    ("🌲", "Verdant Overwatch", "Bioluminescent spores swirl between ancient trunks."),
    ("🌊", "Tidal Resonance", "Moonlit surf crashes against crystalline caverns."),
    ("🌌", "Starfall Ridge", "Meteor dust drifts across a gravity-light plateau."),
    ("🌋", "Magma Corridor", "Vents pulse underfoot with primal, red-hot rhythm."),
    ("❄️", "Aurora Chasm", "Iridescent ice mirrors every motion in prismatic streaks."),
    ("⚙️", "Celadon Manufactory", "Servo arms reset the battlefield between each exchange."),
]

BRANCH_TWISTS = [
    "An allied scout flags a terrain hazard rewriting initiative order.",
    "Wild support units stir in the periphery, ready to tip the balance.",
    "A timed supply drop hums overhead, promising backup if you hold out.",
    "Telemetry pings a sudden weather flux altering move potency.",
    "Command authorises prototype gear if you can stall three turns.",
    "A rival operative shadows the encounter, eager to intercept your claim.",
]

TACTIC_LOADOUTS = [
    {
        "icon": "🎯",
        "title": "Deploy Quick Ball Salvo",
        "success": "The {target} is secured in a double-shake snap while cheers erupt across comms.",
        "fallback": "{pokemon} slips free in a burst of light, boosting its Evasion and tempo.",
    },
    {
        "icon": "🛡️",
        "title": "Raise Reflective Barriers",
        "success": "Screens crystallise, letting you pace the fight and open a safe capture window.",
        "fallback": "Barrier harmonics misalign, giving {pokemon} a free setup turn to escalate pressure.",
    },
    {
        "icon": "⚡",
        "title": "Trigger Overclocked Strike Team",
        "success": "Coordinated assaults land clean, dropping {pokemon}'s stamina into the red immediately.",
        "fallback": "Overclock feedback rattles your squad, forcing a swap while {pokemon} rallies.",
    },
    {
        "icon": "🪬",
        "title": "Invoke Terrain Sync Protocol",
        "success": "Terrain energy bends toward you, amplifying status plays that pacify the target.",
        "fallback": "The sync desyncs, amplifying {pokemon}'s innate typing instead.",
    },
    {
        "icon": "🛰️",
        "title": "Call Orbital Survey Assist",
        "success": "Satellite intel locks patterns, letting you predict every counter-move perfectly.",
        "fallback": "A solar flare knocks the feed offline, leaving you momentarily exposed.",
    },
]

MEGA_NAME_OVERRIDES = {
    "mega charizard x": "charizard-mega-x",
    "mega charizard y": "charizard-mega-y",
    "mega mewtwo x": "mewtwo-mega-x",
    "mega mewtwo y": "mewtwo-mega-y",
}


def normalize_pokemon_identifier(pokemon_name: str) -> str:
    """Return an API-friendly identifier for PokéAPI lookups."""

    lower_name = pokemon_name.lower().strip()
    if lower_name in MEGA_NAME_OVERRIDES:
        return MEGA_NAME_OVERRIDES[lower_name]

    if lower_name.startswith("mega "):
        suffix = lower_name.replace("mega ", "", 1)
        suffix = suffix.replace(" ", "-")
        return f"{suffix}-mega"

    return lower_name.replace(" ", "-")


def get_version_priority(version_name: str) -> int:
    """Return an ordering hint for move version groups."""

    try:
        return VERSION_PRIORITY.index(version_name)
    except ValueError:
        return len(VERSION_PRIORITY)


def fetch_move_metadata(move_url: str) -> dict:
    """Fetch minimal metadata for a move with caching."""

    if move_url in MOVE_CACHE:
        return MOVE_CACHE[move_url]

    try:
        with urllib.request.urlopen(move_url, timeout=5) as response:
            payload = json.loads(response.read().decode())
    except Exception as exc:  # pragma: no cover - defensive against flaky API
        print(f"Warning: Could not fetch move data from {move_url}: {exc}")
        payload = {}

    metadata = {
        "type": payload.get("type", {}).get("name"),
        "power": payload.get("power"),
        "damage_class": payload.get("damage_class", {}).get("name"),
    }
    MOVE_CACHE[move_url] = metadata
    time.sleep(0.1)
    return metadata


def select_signature_moves(api_moves: list, pokemon_types: list[str], pokemon_stats: dict) -> list[dict]:
    """Return a curated set of competitive moves for display."""

    scored_moves = []
    seen_moves: set[str] = set()

    # Determine if Pokemon is physical or special attacker
    attack = pokemon_stats.get('attack', 0)
    sp_attack = pokemon_stats.get('special-attack', 0)
    is_physical = attack > sp_attack

    for entry in api_moves:
        move_name = entry.get("move", {}).get("name")
        move_url = entry.get("move", {}).get("url")
        if not move_name or not move_url or move_name in seen_moves:
            continue

        # Skip terrible moves
        if move_name in BAD_MOVES:
            continue

        version_details = entry.get("version_group_details", [])
        if not version_details:
            continue

        eligible_details = [
            detail
            for detail in version_details
            if detail.get("move_learn_method", {}).get("name") in MOVE_METHOD_PRIORITY
        ]
        if not eligible_details:
            continue

        best_detail = min(
            eligible_details,
            key=lambda detail: (
                get_version_priority(detail.get("version_group", {}).get("name", "")),
                MOVE_METHOD_PRIORITY.get(detail.get("move_learn_method", {}).get("name", ""), 99),
                -detail.get("level_learned_at", 0),
            ),
        )

        seen_moves.add(move_name)
        scored_moves.append(
            (
                get_version_priority(best_detail.get("version_group", {}).get("name", "")),
                MOVE_METHOD_PRIORITY.get(best_detail.get("move_learn_method", {}).get("name", ""), 99),
                -best_detail.get("level_learned_at", 0),
                move_name,
                move_url,
                best_detail,
            )
        )

    if not scored_moves:
        return []

    scored_moves.sort(key=lambda item: item[:4])
    trimmed_moves = scored_moves[:50]  # Increased pool for better selection

    candidates: list[dict] = []
    for _, _, _, move_name, move_url, best_detail in trimmed_moves:
        metadata = fetch_move_metadata(move_url)
        move_type = metadata.get("type")
        power = metadata.get("power") or 0
        damage_class = metadata.get("damage_class", "status")

        candidates.append(
            {
                "name": move_name.replace("-", " ").title(),
                "raw_name": move_name,
                "type": move_type,
                "power": power,
                "damage_class": damage_class,
                "method": best_detail.get("move_learn_method", {}).get("name", "unknown"),
                "level": best_detail.get("level_learned_at", 0),
            }
        )

    if not candidates:
        return []

    def move_sort_key(item: dict) -> tuple:
        move_raw = item.get("raw_name", "")
        
        # Highest priority: competitive utility moves
        is_priority = 0 if move_raw in COMPETITIVE_PRIORITY_MOVES else 1
        
        # STAB bonus
        stab = 0 if item.get("type") in pokemon_types else 1
        
        # Match damage class to Pokemon's attacking stat
        damage_class = item.get("damage_class", "status")
        class_mismatch = 0
        if damage_class == "physical" and not is_physical:
            class_mismatch = 1
        elif damage_class == "special" and is_physical:
            class_mismatch = 1
        
        # Status moves are valuable
        damage_bias = 0 if damage_class == "status" else 1
        
        method_bias = MOVE_METHOD_PRIORITY.get(item.get("method"), 99)
        
        return (
            is_priority,        # Competitive moves first
            class_mismatch,     # Match attack stat
            -stab,              # STAB preferred
            damage_bias,        # Include status moves
            method_bias,        # Learn method
            -item.get("power", 0),  # Higher power
            -item.get("level", 0),
            item.get("name", ""),
        )

    candidates.sort(key=move_sort_key)
    return candidates[:4]


def select_competitive_nature(stats: dict) -> str:
    """Select optimal nature based on Pokemon's stat distribution."""
    if not stats:
        return 'Serious'
    
    attack = stats.get('attack', 0)
    sp_attack = stats.get('special-attack', 0)
    defense = stats.get('defense', 0)
    sp_defense = stats.get('special-defense', 0)
    speed = stats.get('speed', 0)
    hp = stats.get('hp', 0)
    
    # Determine primary attacking stat
    is_physical = attack > sp_attack
    is_special = sp_attack > attack
    is_mixed = abs(attack - sp_attack) < 20
    
    # Fast physical attacker
    if is_physical and speed >= 100:
        return 'Jolly'  # +Speed, -SpAtk
    # Slow physical attacker
    elif is_physical and speed < 100:
        return 'Adamant'  # +Attack, -SpAtk
    # Fast special attacker
    elif is_special and speed >= 100:
        return 'Timid'  # +Speed, -Attack
    # Slow special attacker
    elif is_special and speed < 100:
        return 'Modest'  # +SpAtk, -Attack
    # Defensive physical
    elif defense > sp_defense and speed < 90:
        return 'Impish'  # +Defense, -SpAtk
    # Defensive special
    elif sp_defense > defense and speed < 90:
        return 'Careful'  # +SpDef, -SpAtk
    # Mixed attacker
    elif is_mixed:
        return 'Hasty' if speed >= 100 else 'Mild'
    
    return 'Serious'  # Neutral


def select_competitive_ability(pokemon_name: str, abilities: list[str]) -> str:
    """Select best competitive ability for a Pokemon."""
    if not abilities:
        return 'Unknown'
    
    # Normalize pokemon name for lookup
    normalized_name = pokemon_name.lower().replace(' ', '-')
    base_name = normalized_name.replace('mega-', '').replace('-mega', '')
    
    # Check if we have preferred abilities for this Pokemon
    if base_name in COMPETITIVE_ABILITIES:
        preferred = COMPETITIVE_ABILITIES[base_name]
        for ability in abilities:
            normalized_ability = ability.lower().replace(' ', '-')
            if normalized_ability in preferred:
                return ability
    
    # Default to first ability
    return abilities[0]


def select_competitive_item(stats: dict, role: str) -> str:
    """Select optimal held item based on Pokemon's role."""
    if not stats:
        return 'Leftovers'
    
    attack = stats.get('attack', 0)
    sp_attack = stats.get('special-attack', 0)
    defense = stats.get('defense', 0)
    sp_defense = stats.get('special-defense', 0)
    speed = stats.get('speed', 0)
    hp = stats.get('hp', 0)
    
    # High speed offensive
    if speed >= 110 and (attack >= 120 or sp_attack >= 120):
        return random.choice(['Life Orb', 'Choice Specs' if sp_attack > attack else 'Choice Band'])
    
    # Medium speed offensive
    elif speed >= 80 and (attack >= 100 or sp_attack >= 100):
        return random.choice(['Choice Scarf', 'Expert Belt', 'Life Orb'])
    
    # Defensive/tank
    elif (defense + sp_defense) >= 180:
        return random.choice(['Leftovers', 'Heavy-Duty Boots', 'Assault Vest'])
    
    # Glass cannon
    elif hp < 80 and (attack >= 130 or sp_attack >= 130):
        return random.choice(['Focus Sash', 'Life Orb'])
    
    # Balanced
    else:
        return random.choice(['Leftovers', 'Heavy-Duty Boots', 'Life Orb'])


def analyze_team_weaknesses(team_types: dict) -> dict:
    """Analyze team's defensive weaknesses based on type chart."""
    # Simplified type chart - defensive matchups
    type_chart = {
        'normal': {'fighting': 2},
        'fire': {'water': 2, 'ground': 2, 'rock': 2},
        'water': {'electric': 2, 'grass': 2},
        'electric': {'ground': 2},
        'grass': {'fire': 2, 'ice': 2, 'poison': 2, 'flying': 2, 'bug': 2},
        'ice': {'fire': 2, 'fighting': 2, 'rock': 2, 'steel': 2},
        'fighting': {'flying': 2, 'psychic': 2, 'fairy': 2},
        'poison': {'ground': 2, 'psychic': 2},
        'ground': {'water': 2, 'grass': 2, 'ice': 2},
        'flying': {'electric': 2, 'ice': 2, 'rock': 2},
        'psychic': {'bug': 2, 'ghost': 2, 'dark': 2},
        'bug': {'fire': 2, 'flying': 2, 'rock': 2},
        'rock': {'water': 2, 'grass': 2, 'fighting': 2, 'ground': 2, 'steel': 2},
        'ghost': {'ghost': 2, 'dark': 2},
        'dragon': {'ice': 2, 'dragon': 2, 'fairy': 2},
        'dark': {'fighting': 2, 'bug': 2, 'fairy': 2},
        'steel': {'fire': 2, 'fighting': 2, 'ground': 2},
        'fairy': {'poison': 2, 'steel': 2},
    }
    
    weakness_count = {}
    
    # Count how many Pokemon are weak to each type
    for pokemon_types in team_types.values():
        for ptype in pokemon_types:
            if ptype in type_chart:
                for weakness_type, multiplier in type_chart[ptype].items():
                    weakness_count[weakness_type] = weakness_count.get(weakness_type, 0) + 1
    
    # Find critical weaknesses (3+ Pokemon weak)
    critical_weaknesses = {t: count for t, count in weakness_count.items() if count >= 3}
    moderate_weaknesses = {t: count for t, count in weakness_count.items() if count == 2}
    
    return {
        'critical': critical_weaknesses,
        'moderate': moderate_weaknesses,
        'all': weakness_count
    }


def calculate_evs(stats: dict, role: str) -> dict:
    """Calculate optimal EV spread based on stats and role."""
    if not stats:
        return {'HP': 0, 'Atk': 0, 'Def': 0, 'SpA': 0, 'SpD': 0, 'Spe': 0}
    
    attack = stats.get('attack', 0)
    sp_attack = stats.get('special-attack', 0)
    speed = stats.get('speed', 0)
    defense = stats.get('defense', 0)
    sp_defense = stats.get('special-defense', 0)
    
    is_physical = attack > sp_attack
    is_fast = speed >= 100
    
    # Offensive spread
    if is_physical and is_fast:
        return {'HP': 0, 'Atk': 252, 'Def': 4, 'SpA': 0, 'SpD': 0, 'Spe': 252}
    elif is_physical and not is_fast:
        return {'HP': 252, 'Atk': 252, 'Def': 4, 'SpA': 0, 'SpD': 0, 'Spe': 0}
    elif not is_physical and is_fast:
        return {'HP': 0, 'Atk': 0, 'Def': 0, 'SpA': 252, 'SpD': 4, 'Spe': 252}
    elif not is_physical and not is_fast:
        return {'HP': 252, 'Atk': 0, 'Def': 0, 'SpA': 252, 'SpD': 4, 'Spe': 0}
    
    # Defensive spread
    if defense > sp_defense:
        return {'HP': 252, 'Atk': 0, 'Def': 252, 'SpA': 0, 'SpD': 4, 'Spe': 0}
    else:
        return {'HP': 252, 'Atk': 0, 'Def': 4, 'SpA': 0, 'SpD': 252, 'Spe': 0}


def fetch_pokemon_data(pokemon_name: str, original_name: Optional[str] = None):
    """Fetch Pokémon data from PokéAPI"""
    try:
        identifier = normalize_pokemon_identifier(pokemon_name)
        url = f"https://pokeapi.co/api/v2/pokemon/{identifier}"
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
        
        pokemon_types = [t['type']['name'] for t in data['types']]
        stats = {s['stat']['name']: s['base_stat'] for s in data['stats']}
        signature_moves = select_signature_moves(data['moves'], pokemon_types, stats)
        
        # Get all abilities
        all_abilities = [a['ability']['name'].replace('-', ' ').title() for a in data['abilities']]
        
        # Select competitive ability
        best_ability = select_competitive_ability(original_name or data['name'], all_abilities)
        
        # Select competitive nature
        competitive_nature = select_competitive_nature(stats)
        
        # Determine role
        if stats:
            top_stat_key = max(stats, key=stats.get)
            role = ROLE_BY_STAT.get(top_stat_key, 'Balanced Command Core')
        else:
            role = 'Balanced Command Core'
        
        # Select item
        competitive_item = select_competitive_item(stats, role)
        
        # Calculate EVs
        ev_spread = calculate_evs(stats, role)

        return {
            'name': (original_name or data['name']).title(),
            'types': pokemon_types,
            'height': data['height'] / 10,  # Convert to meters
            'weight': data['weight'] / 10,  # Convert to kg
            'stats': stats,
            'abilities': all_abilities,
            'best_ability': best_ability,
            'nature': competitive_nature,
            'item': competitive_item,
            'evs': ev_spread,
            'signature_moves': signature_moves,
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


def create_flux_meter(value, max_value, length=18):
    """Create an over-the-top meter for the dynamism overlay"""
    if max_value <= 0:
        return '[' + '░' * length + '] 0% · STANDBY'

    value = max(value, 0)
    ratio = min(value / max_value, 1)
    filled = int(round(ratio * length))
    filled = max(0, min(length, filled))
    bar = '[' + '▓' * filled + '░' * (length - filled) + ']'

    if ratio >= 0.9:
        mode = "Ω-OVERDRIVE"
    elif ratio >= 0.7:
        mode = "VORTEX"
    elif ratio >= 0.5:
        mode = "CRUISE"
    elif ratio > 0:
        mode = "WARMUP"
    else:
        mode = "STANDBY"

    return f"{bar} {ratio * 100:4.0f}% · {mode}"

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

def pick_index(n: int, day_seed: int) -> int:
    """Deterministic by date: different one each day"""

    if n == 0:
        return 0
    return day_seed % n


def roll_random_encounter():
    """Roll a random encounter with chances for legendary sightings and shiny triggers."""
    legendary_cutoff = 0.12
    roll = random.random()

    if roll < legendary_cutoff:
        pool = LEGENDARY_ROSTER
        rarity = "Legendary Sighting"
        callout = "Ultra-rare beacon detected—Command approves immediate containment."
    else:
        pool = WILD_ROSTER
        rarity = "Wild Encounter"
        callout = "Routine scouting ping—deploy capture drones at your discretion."

    species = random.choice(pool)
    shiny_roll = random.random()
    is_shiny = shiny_roll < SHINY_TRIGGER_RATE

    if is_shiny:
        callout += " ✨ Shiny trigger tripped!"

    return species, rarity, callout, is_shiny


def describe_target(is_shiny: bool, legendary_mode: bool) -> str:
    """Return flavour text describing the encounter target."""
    if is_shiny:
        return "shimmering anomaly"
    if legendary_mode:
        return "legendary beacon"
    return "wild signal"


def generate_branching_paths(species: str, pokemon_info: Optional[dict], is_shiny: bool, legendary_mode: bool) -> str:
    """Create a branching, click-to-choose set of encounter paths for the README."""
    display_name = species.title()
    type_summary = None
    if pokemon_info and pokemon_info.get("types"):
        type_summary = " / ".join([t.title() for t in pokemon_info["types"]])

    target_descriptor = describe_target(is_shiny, legendary_mode)
    legend_tag = "Legendary-class" if legendary_mode else "Wild-class"
    shiny_suffix = " with radiant sheen" if is_shiny else ""
    twist_pool = random.sample(BRANCH_TWISTS, k=3)
    path_pool = random.sample(BRANCH_PATHS, k=3)

    path_blocks = []
    for idx, ((emoji, title, description), twist) in enumerate(zip(path_pool, twist_pool), start=1):
        tactic_left, tactic_right = random.sample(TACTIC_LOADOUTS, k=2)
        odds_left = random.randint(58, 92)
        odds_right = random.randint(54, 88)

        type_line = f"  - **Type Intel:** {type_summary}" if type_summary else ""
        header = f"<details>\n  <summary>{emoji} Path {idx} — {title}</summary>\n\n"
        body_lines = [
            f"  - **Battlefield State:** {description}",
            f"  - **Encounter Twist:** {twist}",
            f"  - **Command Brief:** Track the {legend_tag} target — {display_name} ({target_descriptor}{shiny_suffix}).",
        ]
        if type_line:
            body_lines.append(type_line)

        def render_tactic(tactic: dict, odds: int) -> str:
            success_line = tactic["success"].format(target=target_descriptor, pokemon=display_name)
            fallback_line = tactic["fallback"].format(pokemon=display_name)
            return (
                "  <details>\n"
                f"    <summary>{tactic['icon']} {tactic['title']} · {odds}% odds</summary>\n\n"
                f"    - **If it lands:** {success_line}\n"
                f"    - **If it whiffs:** {fallback_line}\n"
                "  </details>"
            )

        tactics_block = "\n".join([
            render_tactic(tactic_left, odds_left),
            render_tactic(tactic_right, odds_right),
        ])

        path_block = header + "\n".join(body_lines) + "\n\n" + tactics_block + "\n</details>"
        path_blocks.append(path_block)

    return "\n\n".join(path_blocks)


root = os.path.dirname(os.path.dirname(__file__))

# Load archetypes
with open(os.path.join(root, "data", "archetypes.json")) as f:
    arc = json.load(f)

now_utc = datetime.datetime.now(datetime.UTC)
day_number = now_utc.date().toordinal()

idx = pick_index(len(arc), day_number)
chosen = arc[idx]

random_seed_basis = f"{day_number}-{chosen.get('id', idx)}"
random.seed(random_seed_basis)

print(f"🎯 Building README for archetype: {chosen['title']}")
print(f"👑 Team Leader: {chosen['lead']}")

# Fetch Pokémon data
print("\n🔍 Fetching Pokémon data from PokéAPI...")
pokemon_data = {}
for pokemon_name in chosen['team']:
    print(f"  📡 Fetching {pokemon_name}...")
    data = fetch_pokemon_data(pokemon_name, original_name=pokemon_name)
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
            'signature_moves': [
                {'name': 'Tackle', 'type': 'normal', 'power': 40, 'damage_class': 'physical', 'method': 'level-up', 'level': 1},
                {'name': 'Quick Attack', 'type': 'normal', 'power': 40, 'damage_class': 'physical', 'method': 'level-up', 'level': 5},
                {'name': 'Hyper Beam', 'type': 'normal', 'power': 150, 'damage_class': 'special', 'method': 'machine', 'level': 0},
                {'name': 'Rest', 'type': 'psychic', 'power': 0, 'damage_class': 'status', 'method': 'machine', 'level': 0},
            ],
            'flavor_text': 'A mysterious Pokémon!',
            'sprite': None,
            'shiny_sprite': None,
            'id': 0
        }

# Pick a random Pokémon for the encounter with legendary and shiny dynamics
random_choice, encounter_rarity, encounter_callout, encounter_is_shiny = roll_random_encounter()
shiny_suffix = " (shiny)" if encounter_is_shiny else ""
print(
    f"\n✨ Random encounter: {random_choice.title()}{shiny_suffix} [{encounter_rarity}]"
)
random_pokemon_data = fetch_pokemon_data(random_choice, original_name=random_choice)
branching_paths_block = generate_branching_paths(
    random_choice,
    random_pokemon_data,
    encounter_is_shiny,
    encounter_rarity == "Legendary Sighting",
)

# Load template
with open(os.path.join(root, "README.template.md")) as f:
    template = f.read()

# Current date info
current_date = now_utc.strftime("%Y-%m-%d %H:%M UTC")

# Get lead Pokémon data
lead_name = chosen['lead']
lead_data = pokemon_data.get(lead_name, {})

# Prepare lead Pokémon info
lead_types = ' '.join([get_type_emoji(t) + t.upper() for t in lead_data.get('types', ['normal'])])
lead_ability = lead_data.get('best_ability', lead_data.get('abilities', ['Unknown'])[0])
lead_nature = lead_data.get('nature', 'Serious')
lead_item = lead_data.get('item', 'Leftovers')
lead_evs = lead_data.get('evs', {})
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

lead_bst = sum([lead_hp, lead_attack, lead_defense, lead_spatk, lead_spdef, lead_speed])

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
team_types_by_pokemon = {}
team_dossiers = []
fastest_member = (None, {'stats': {'speed': 0}})
heaviest_member = (None, {'weight': 0})
bst_member = (None, 0)
total_speed = 0
team_bst_total = 0

for pokemon_name in chosen['team']:
    pdata = pokemon_data.get(pokemon_name, {})
    stats = pdata.get('stats', {})
    types = pdata.get('types', ['normal'])
    abilities = pdata.get('abilities', ['Unknown'])
    signature_moves = pdata.get('signature_moves') or []
    sprite_html = get_pokemon_sprite_html(pdata.get('sprite'), pokemon_name, 160)

    team_types_by_pokemon[pokemon_name] = types
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

    team_bst_total += bst

    total_speed += speed_value

    top_stat_key = max(stats, key=stats.get) if stats else 'hp'
    top_stat_value = stats.get(top_stat_key, 0)
    top_stat_label = top_stat_key.replace('-', ' ').title()
    role = ROLE_BY_STAT.get(top_stat_key, 'Balanced Command Core')

    formatted_moves = []
    for move in signature_moves:
        move_type = move.get('type', 'normal')
        emoji = get_type_emoji(move_type)
        power = move.get('power', 0)
        if power:
            power_text = f"{power} BP"
        else:
            power_text = "Utility"
        damage_class = move.get('damage_class', 'status').replace('-', ' ').title()
        formatted_moves.append(
            f"  - {emoji} {move.get('name', 'Unknown')} · {damage_class} · {power_text}"
        )

    move_lines = "\n".join(formatted_moves) if formatted_moves else "  - (pending scouting)"
    
    # Get competitive info
    best_ability = pdata.get('best_ability', abilities[0] if abilities else 'Unknown')
    nature = pdata.get('nature', 'Serious')
    item = pdata.get('item', 'Leftovers')
    evs = pdata.get('evs', {})
    
    # Format EV spread
    ev_parts = []
    for stat_name, ev_value in evs.items():
        if ev_value > 0:
            ev_parts.append(f"{ev_value} {stat_name}")
    ev_spread_text = " / ".join(ev_parts) if ev_parts else "0 / 0 / 0 / 0 / 0 / 0"

    dossier = (
        f"<details open>\n"
        f"<summary>⚔️ <strong>{pokemon_name}</strong> · "
        + " / ".join([get_type_emoji(t) + t.upper() for t in types])
        + "</summary>\n\n"
        f"<div align=\"center\">\n{sprite_html}\n</div>\n\n"
        f"- **Base Stat Total:** {bst}\n"
        f"- **Top Stat:** {top_stat_label} ({top_stat_value})\n"
        f"- **Battle Role:** {role}\n"
        f"- **Ability:** {best_ability}\n"
        f"- **Nature:** {nature}\n"
        f"- **Held Item:** {item}\n"
        f"- **EV Spread:** {ev_spread_text}\n"
        f"- **Signature Moves:**\n{move_lines}\n"
        f"</details>"
    )
    team_dossiers.append(dossier)

    pokemon_data[pokemon_name]['role'] = role

unique_type_count = len(team_type_counts)
average_speed = (total_speed / len(chosen['team'])) if chosen['team'] else 0
fastest_name = fastest_member[0] or 'Unknown'
fastest_speed = fastest_member[1]['stats'].get('speed', 0) if fastest_member[0] else 0
heaviest_name = heaviest_member[0] or 'Unknown'
heaviest_weight = heaviest_member[1].get('weight', 0) if heaviest_member[0] else 0
highest_bst_name = bst_member[0] or 'Unknown'
highest_bst_value = bst_member[1]

max_team_bst = max(1, len(chosen['team'])) * 720
power_level = team_bst_total
power_gauge = create_power_gauge(power_level, max_value=max_team_bst)

coverage_lines = []
for t_name, count in sorted(team_type_counts.items(), key=lambda item: (-item[1], item[0])):
    coverage_lines.append(f"- {get_type_emoji(t_name)} **{t_name.upper()}** ×{count}")
type_coverage_block = "\n".join(coverage_lines) if coverage_lines else "- Coverage telemetry unavailable"

# Analyze team weaknesses
weakness_analysis = analyze_team_weaknesses(team_types_by_pokemon)
critical_weaknesses = weakness_analysis['critical']
moderate_weaknesses = weakness_analysis['moderate']

weakness_lines = []
if critical_weaknesses:
    weakness_lines.append("### ⚠️ Critical Weaknesses (3+ Pokemon)")
    for wtype, count in sorted(critical_weaknesses.items(), key=lambda x: -x[1]):
        weakness_lines.append(f"- {get_type_emoji(wtype)} **{wtype.upper()}** threatens {count} team members")

if moderate_weaknesses:
    weakness_lines.append("\n### ⚡ Moderate Weaknesses (2 Pokemon)")
    for wtype, count in sorted(moderate_weaknesses.items(), key=lambda x: -x[1]):
        weakness_lines.append(f"- {get_type_emoji(wtype)} **{wtype.upper()}** hits {count} team members")

if not weakness_lines:
    weakness_lines.append("✅ No critical type weaknesses detected — balanced defensive coverage.")

weakness_block = "\n".join(weakness_lines)

# Hyper-dynamic analytics and presentation flair
team_size = len(chosen['team']) if chosen.get('team') else 0
synergy_meter = create_flux_meter(unique_type_count, team_size or 1)
speed_pulse = create_flux_meter(average_speed, 180)
bst_overdrive = create_flux_meter(highest_bst_value, 720)

if average_speed >= 130:
    tempo_callsign = "Chrono-stream locked: squad bends turns before they exist."
elif average_speed >= 110:
    tempo_callsign = "Velocity nets deployed—tempo advantage sustained."
elif average_speed >= 90:
    tempo_callsign = "Adaptive cadence engaged; striking windows recalibrated live."
else:
    tempo_callsign = "Glacial recon mode; compensating via formation traps."

hyperstream_metrics = [
    f"- **Synergy Mesh:** {unique_type_count}/{team_size or 1} typings interlaced across the roster.",
    f"- **Velocity Drift:** Average speed {average_speed:.1f} with {fastest_name} spiking {fastest_speed}.",
    f"- **Apex Pressure:** {highest_bst_name} anchors {highest_bst_value} BST saturation."
]
hyperstream_block = "\n".join(hyperstream_metrics)

bonkers_taglines = [
    "synthetic battle intel streamed straight from Kanto Mission Control",
    "orchestrated like a championship draft board with neon command prompts",
    "tuned for data maximalists chasing legendary-level dashboards",
    "pulling PokéAPI signals into a holo-briefing worthy of a League HQ",
    "hyperlattice uplink thrumming with chrono-synced PokéAPI echoes",
    "battle telemetry screaming through neon conduits in full-spectrum chaos"
]
bonkers_tagline = random.choice(bonkers_taglines)

lead_stat_map = {
    'attack': lead_attack,
    'special-attack': lead_spatk,
    'defense': lead_defense,
    'special-defense': lead_spdef,
    'speed': lead_speed
}
lead_dominant_stat = max(lead_stat_map, key=lead_stat_map.get)
lead_role = ROLE_BY_STAT.get(lead_dominant_stat, 'Balanced Command Core')

analytics_blurb = (
    f"{lead_name} fronts a {len(chosen['team'])}-unit strike team spanning {unique_type_count} unique typings "
    f"with an average Speed index of {average_speed:.1f}. Fastest scout: {fastest_name} ({fastest_speed} Speed)."
)

lead_signature_moves = lead_data.get('signature_moves') or []
lead_move_lines = []
for move in lead_signature_moves:
    move_type = (move.get('type') or 'unknown').upper()
    emoji = get_type_emoji(move.get('type', 'normal'))
    power_value = move.get('power', 0)
    power_text = f"{power_value} BP" if power_value else "Utility"
    damage_class = move.get('damage_class', 'status').replace('-', ' ').title()
    lead_move_lines.append(
        f"- **{move.get('name', 'Unknown')}** · {emoji} {move_type} · {damage_class} · {power_text}"
    )

if not lead_move_lines:
    lead_move_lines = ["- Recon uplink pending—signature arsenal unavailable."]

lead_moves_block = "\n".join(lead_move_lines)

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
    '{LEAD_ITEM}': lead_item,
    '{LEAD_EVS}': ' / '.join([f"{v} {k}" for k, v in lead_evs.items() if v > 0]) if lead_evs else '0/0/0/0/0/0',
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
    '{LEAD_MOVES}': lead_moves_block,
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
    '{WEAKNESS_ANALYSIS}': weakness_block,
    '{SYNERGY_METER}': synergy_meter,
    '{SPEED_PULSE}': speed_pulse,
    '{BST_OVERDRIVE}': bst_overdrive,
    '{TEMPO_CALLSIGN}': tempo_callsign,
    '{HYPERSTREAM_BLOCK}': hyperstream_block,
    '{BRANCHING_STORY_BLOCK}': branching_paths_block,
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
    replacements[f'{{POKEMON_{i}_ROLE}}'] = pdata.get('role', 'Adaptive Operative')

legendary_mode = encounter_rarity == "Legendary Sighting"
display_name = random_choice.upper()

if encounter_is_shiny:
    encounter_summary = f"✨ SHINY ALERT: {display_name}"
elif legendary_mode:
    encounter_summary = f"🌌 LEGENDARY SIGHTING: {display_name}"
else:
    encounter_summary = f"🎲 WILD ENCOUNTER: {display_name}"

if encounter_is_shiny:
    shiny_trigger_panel = (
        "<details open>\n"
        "<summary>✨ Shiny Trigger Online</summary>\n\n"
        "- Status: ✅ Sparkle state locked in for this cycle.\n"
        "- Tip: Archive the sprite before the glow collapses.\n"
        "</details>"
    )
else:
    charge_level = random.randint(25, 92)
    shiny_trigger_panel = (
        "<details>\n"
        "<summary>✨ Prime the Shiny Trigger</summary>\n\n"
        f"- Status: ⏳ Charge holding at {charge_level}%.\n"
        "- Tip: Refresh the Command Center to reroll the pulse.\n"
        "</details>"
    )

replacements['{ENCOUNTER_SUMMARY}'] = encounter_summary
replacements['{ENCOUNTER_RARITY}'] = encounter_rarity
replacements['{ENCOUNTER_SIGNAL}'] = encounter_callout
replacements['{SHINY_TRIGGER_PANEL}'] = shiny_trigger_panel

# Random Pokémon encounter
if random_pokemon_data:
    random_types = ' '.join([get_type_emoji(t) + t.upper() for t in random_pokemon_data.get('types', ['normal'])])
    sprite_source = random_pokemon_data.get('sprite')
    if encounter_is_shiny and random_pokemon_data.get('shiny_sprite'):
        sprite_source = random_pokemon_data.get('shiny_sprite')
    replacements['{RANDOM_POKEMON}'] = random_pokemon_data['name'].upper()
    replacements['{RANDOM_POKEMON_ASCII}'] = get_pokemon_sprite_html(sprite_source, random_pokemon_data['name'], 150)
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
