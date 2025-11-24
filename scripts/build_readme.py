#!/usr/bin/env python3
import json
import os
import datetime
import random
import re
import urllib.request
import urllib.error
import time
import math
from typing import Optional, List, Dict, Tuple

# Import local modules
try:
    import svg_generator
    import github_stats
    import shiny_hunt
    import image_compositor
    import coach_ai
except ImportError as e:
    print(f"Warning: Optional modules failed to import: {e}")
    svg_generator = None
    github_stats = None
    shiny_hunt = None
    image_compositor = None
    coach_ai = None

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

# Competitive move priority
COMPETITIVE_PRIORITY_MOVES = {
    'stealth-rock', 'spikes', 'toxic-spikes', 'sticky-web',
    'rapid-spin', 'defog',
    'will-o-wisp', 'thunder-wave', 'toxic', 'spore', 'sleep-powder', 'yawn',
    'protect', 'detect', 'substitute', 'roost', 'recover', 'synthesis', 'moonlight', 'soft-boiled', 'morning-sun',
    'u-turn', 'volt-switch', 'flip-turn', 'teleport', 'parting-shot',
    'knock-off', 'taunt', 'encore', 'disable',
    'aqua-jet', 'mach-punch', 'bullet-punch', 'ice-shard', 'shadow-sneak',
    'accelerock', 'sucker-punch', 'extreme-speed', 'first-impression',
    'swords-dance', 'dragon-dance', 'nasty-plot', 'calm-mind', 'bulk-up',
    'quiver-dance', 'shell-smash', 'shift-gear', 'belly-drum', 'coil',
    'earthquake', 'close-combat', 'flare-blitz', 'hydro-pump', 'ice-beam',
    'thunderbolt', 'psychic', 'shadow-ball', 'dragon-claw', 'dragon-pulse',
    'outrage', 'draco-meteor', 'flamethrower', 'surf', 'scald', 'moonblast',
    'play-rough', 'brave-bird', 'hurricane', 'sludge-bomb', 'sludge-wave',
    'leaf-storm', 'power-whip', 'stone-edge', 'flash-cannon',
}

BAD_MOVES = {
    'constrict', 'lick', 'pound', 'scratch', 'tackle', 'confusion',
    'absorb', 'mega-punch', 'mega-kick', 'sonic-boom', 'dragon-rage',
    'fury-attack', 'comet-punch', 'barrage', 'vice-grip', 'cut', 'fly',
    'strength', 'rock-smash', 'flash', 'struggle', 'splash', 'celebrate',
    'happy-hour', 'hold-hands',
}

COMPETITIVE_ABILITIES = {
    'metagross': ['tough-claws', 'clear-body'],
    'gengar': ['cursed-body', 'levitate', 'shadow-tag'],
    'rayquaza': ['air-lock', 'delta-stream'],
    'zeraora': ['volt-absorb'],
    'noivern': ['infiltrator', 'frisk'],
    'decidueye': ['long-reach', 'overgrow'],
    'dragonite': ['multiscale'],
    'gyarados': ['moxie', 'intimidate'],
    'charizard': ['solar-power', 'drought'],
    'lucario': ['justified', 'inner-focus'],
}

COMPETITIVE_ITEMS = {
    'offensive': ['Choice Band', 'Choice Specs', 'Life Orb', 'Choice Scarf', 'Expert Belt', 'White Herb'],
    'defensive': ['Leftovers', 'Heavy-Duty Boots', 'Rocky Helmet', 'Assault Vest', 'Black Sludge'],
    'utility': ['Focus Sash', 'Mental Herb', 'Light Clay', 'Eject Button', 'Red Card'],
}

MOVE_CACHE: dict[str, dict] = {}

ROLE_BY_STAT = {
    'attack': 'Hyper-Offense Spearhead',
    'special-attack': 'Arcane Artillery Node',
    'defense': 'Fortified Bulwark Unit',
    'special-defense': 'Psi-Shield Anchor',
    'speed': 'Supersonic Initiator',
}

POKEMON_ASCII_ART = {
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
    "mewtwo", "lugia", "ho-oh", "rayquaza", "dialga", "palkia", "giratina",
    "reshiram", "zekrom", "xerneas", "yveltal", "zacian", "zamazenta", "eternatus",
]

WILD_ROSTER = [
    "ditto", "pikachu", "eevee", "snorlax", "magikarp", "gyarados", "dragonite",
    "lucario", "gardevoir", "tyranitar", "garchomp", "dragapult", "mienshao",
    "mimikyu", "noivern", "zeraora", "scizor", "rotom", "volcarona", "greninja"
]

SHINY_TRIGGER_RATE = 1 / 48

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

root = os.path.dirname(os.path.dirname(__file__))

# ==========================================
# ADVANCED GAME ENGINES
# ==========================================

class WeatherSystem:
    WEATHER_TYPES = [
        {"name": "Clear Skies", "emoji": "☀️", "effect": "Standard battle conditions."},
        {"name": "Harsh Sunlight", "emoji": "🔥", "effect": "Fire moves boosted 50%, Water moves weakened 50%."},
        {"name": "Rain", "emoji": "🌧️", "effect": "Water moves boosted 50%, Fire moves weakened 50%."},
        {"name": "Sandstorm", "emoji": "🏜️", "effect": "Rock types get 50% Sp. Def boost. Chip damage active."},
        {"name": "Snow", "emoji": "❄️", "effect": "Ice types get 50% Def boost."},
    ]

    @staticmethod
    def get_daily_weather(seed):
        random.seed(seed)
        return random.choice(WeatherSystem.WEATHER_TYPES)

class BattleSimulator:
    @staticmethod
    def simulate_battle(user_team_name, rival_name, user_lead):
        # Deterministic simulation based on day
        events = [
            f"⚔️ **Battle Start!** Trainer {user_team_name} vs Rival {rival_name}!",
            f"🔹 **Turn 1:** {user_lead} Mega Evolves and uses **Dragon Ascent**!",
            f"🔸 Rival's Garchomp survives on Focus Sash and uses **Swords Dance**!",
            f"🔹 **Turn 2:** {user_lead} uses **Extreme Speed** for the KO!",
            f"🔸 Rival sends out Tapu Koko. Electric Terrain activates!",
            f"🔹 **Turn 3:** {user_lead} switches to Landorus-T to Intimidate!",
            f"🏆 **Result:** Rival forfeits! **{user_team_name} Wins!**"
        ]
        return "\n".join(events)

class QuestGenerator:
    QUESTS = [
        "Optimize 3 functions to increase Metagross's calculation speed.",
        "Push a commit before noon to outspeed Rival Weavile.",
        "Refactor legacy code to clear Gengar's Cursed Body status.",
        "Add unit tests to strengthen the team's Synergy Mesh.",
        "Review a PR to teach Alakazam 'Future Sight'.",
    ]

    @staticmethod
    def get_daily_quest(seed):
        random.seed(seed)
        return random.choice(QuestGenerator.QUESTS)

class PokePasteGenerator:
    @staticmethod
    def generate_paste(pokemon_list: List[Dict]) -> str:
        paste_lines = []
        for p in pokemon_list:
            name = p['name']
            item = p['item']
            ability = p['best_ability']
            nature = p['nature']
            evs = p['evs']
            moves = [m['name'] for m in p['signature_moves']]

            # Format EV string
            ev_list = []
            for k, v in evs.items():
                if v > 0: ev_list.append(f"{v} {k}")
            ev_str = " / ".join(ev_list)

            block = f"{name} @ {item}\nAbility: {ability}\nEVs: {ev_str}\n{nature} Nature"
            for m in moves:
                block += f"\n- {m}"
            paste_lines.append(block)

        return "\n\n".join(paste_lines)

# ... (Previous helper functions like load_trainer_history, normalize_pokemon_identifier, etc.) ...
def load_trainer_history():
    history_path = os.path.join(root, "data", "trainer_history.json")
    if os.path.exists(history_path):
        with open(history_path) as f:
            return json.load(f)
    return {
        "trainer_name": "Arudchayan",
        "rank": "Rookie",
        "total_battles": 0,
        "wins": 0,
        "losses": 0,
        "badges_earned": 0,
        "pokedex_seen": 0,
        "pokedex_caught": 0
    }

def normalize_pokemon_identifier(pokemon_name: str) -> str:
    lower_name = pokemon_name.lower().strip()
    if lower_name in MEGA_NAME_OVERRIDES:
        return MEGA_NAME_OVERRIDES[lower_name]
    if lower_name.startswith("mega "):
        suffix = lower_name.replace("mega ", "", 1)
        suffix = suffix.replace(" ", "-")
        return f"{suffix}-mega"
    return lower_name.replace(" ", "-")

def get_version_priority(version_name: str) -> int:
    try:
        return VERSION_PRIORITY.index(version_name)
    except ValueError:
        return len(VERSION_PRIORITY)

def fetch_move_metadata(move_url: str) -> dict:
    if move_url in MOVE_CACHE:
        return MOVE_CACHE[move_url]
    try:
        with urllib.request.urlopen(move_url, timeout=5) as response:
            payload = json.loads(response.read().decode())
    except Exception as exc:
        print(f"Warning: Could not fetch move data from {move_url}: {exc}")
        payload = {}
    metadata = {
        "type": payload.get("type", {}).get("name"),
        "power": payload.get("power"),
        "damage_class": payload.get("damage_class", {}).get("name"),
    }
    MOVE_CACHE[move_url] = metadata
    time.sleep(0.05)
    return metadata

def select_signature_moves(api_moves: list, pokemon_types: list[str], pokemon_stats: dict, pokemon_name: str) -> list[dict]:
    # ... (Same as updated previously) ...
    scored_moves = []
    seen_moves: set[str] = set()

    attack = pokemon_stats.get('attack', 0)
    sp_attack = pokemon_stats.get('special-attack', 0)
    is_physical = attack > sp_attack

    forced_moves = set()
    if 'rayquaza' in pokemon_name.lower():
        forced_moves.add('dragon-ascent')

    for entry in api_moves:
        move_name = entry.get("move", {}).get("name")
        move_url = entry.get("move", {}).get("url")
        if not move_name or not move_url or move_name in seen_moves:
            continue

        if move_name in BAD_MOVES and move_name not in forced_moves:
            continue

        version_details = entry.get("version_group_details", [])
        if not version_details:
            continue

        eligible_details = [
            detail for detail in version_details
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
    trimmed_moves = scored_moves[:75]

    candidates: list[dict] = []
    for _, _, _, move_name, move_url, best_detail in trimmed_moves:
        metadata = fetch_move_metadata(move_url)
        move_type = metadata.get("type")
        power = metadata.get("power") or 0
        damage_class = metadata.get("damage_class", "status")

        candidates.append({
            "name": move_name.replace("-", " ").title(),
            "raw_name": move_name,
            "type": move_type,
            "power": power,
            "damage_class": damage_class,
            "method": best_detail.get("move_learn_method", {}).get("name", "unknown"),
            "level": best_detail.get("level_learned_at", 0),
        })

    def move_sort_key(item: dict) -> tuple:
        move_raw = item.get("raw_name", "")
        if move_raw in forced_moves:
            return (-10, 0, 0, 0, 0, 0, 0, "")

        is_priority = 0 if move_raw in COMPETITIVE_PRIORITY_MOVES else 1
        stab = 0 if item.get("type") in pokemon_types else 1
        damage_class = item.get("damage_class", "status")
        class_mismatch = 0
        if damage_class == "physical" and not is_physical:
            class_mismatch = 1
        elif damage_class == "special" and is_physical:
            class_mismatch = 1
        damage_bias = 0 if damage_class == "status" else 1
        return (
            is_priority,
            class_mismatch,
            -stab,
            damage_bias,
            MOVE_METHOD_PRIORITY.get(item.get("method"), 99),
            -item.get("power", 0),
            -item.get("level", 0),
            item.get("name", ""),
        )

    candidates.sort(key=move_sort_key)

    final_moves = []
    final_names = set()

    for m in candidates:
        if m['raw_name'] in forced_moves:
            final_moves.append(m)
            final_names.add(m['raw_name'])

    for m in candidates:
        if len(final_moves) >= 4: break
        if m['raw_name'] not in final_names and m['type'] in pokemon_types and m['damage_class'] != 'status':
            if (is_physical and m['damage_class'] == 'physical') or (not is_physical and m['damage_class'] == 'special'):
                final_moves.append(m)
                final_names.add(m['raw_name'])
                break

    for m in candidates:
        if len(final_moves) >= 4: break
        if m['raw_name'] not in final_names and m['damage_class'] == 'status' and m['raw_name'] in COMPETITIVE_PRIORITY_MOVES:
            final_moves.append(m)
            final_names.add(m['raw_name'])
            break

    for m in candidates:
        if len(final_moves) >= 4: break
        if m['raw_name'] not in final_names:
            final_moves.append(m)
            final_names.add(m['raw_name'])

    return final_moves

# ... (Include other helper functions: select_competitive_nature, select_competitive_ability, etc.) ...
def select_competitive_nature(stats: dict) -> str:
    if not stats: return 'Serious'
    attack = stats.get('attack', 0)
    sp_attack = stats.get('special-attack', 0)
    defense = stats.get('defense', 0)
    sp_defense = stats.get('special-defense', 0)
    speed = stats.get('speed', 0)
    is_physical = attack > sp_attack
    is_special = sp_attack > attack
    is_mixed = abs(attack - sp_attack) < 20
    if is_physical: return 'Jolly' if speed >= 100 else 'Adamant'
    elif is_special: return 'Timid' if speed >= 100 else 'Modest'
    elif is_mixed: return 'Hasty' if speed >= 100 else 'Mild'
    elif defense > sp_defense: return 'Impish'
    else: return 'Careful'

def select_competitive_ability(pokemon_name: str, abilities: list[str]) -> str:
    if not abilities: return 'Unknown'
    normalized_name = pokemon_name.lower().replace(' ', '-')
    base_name = normalized_name.replace('mega-', '').replace('-mega', '')
    if base_name in COMPETITIVE_ABILITIES:
        preferred = COMPETITIVE_ABILITIES[base_name]
        for ability in abilities:
            normalized_ability = ability.lower().replace(' ', '-')
            if normalized_ability in preferred:
                return ability
    return abilities[0]

def select_competitive_item(stats: dict, role: str, pokemon_name: str, types: list[str], archetype_data: dict) -> str:
    if archetype_data.get('mega') and archetype_data.get('lead') == pokemon_name:
        if 'rayquaza' not in pokemon_name.lower():
            return f"{pokemon_name.split()[1]}ite" if 'Mega' in pokemon_name else f"{pokemon_name}ite"
    if archetype_data.get('z_move') and archetype_data.get('lead') == pokemon_name:
        type_name = archetype_data.get('tera_type', 'Normal')
        return f"{type_name}ium Z"
    if not stats: return 'Leftovers'
    attack = stats.get('attack', 0)
    sp_attack = stats.get('special-attack', 0)
    speed = stats.get('speed', 0)
    hp = stats.get('hp', 0)
    weak_to_rocks = False
    for t in types:
        if t in ['fire', 'ice', 'flying', 'bug']:
            weak_to_rocks = True
    if weak_to_rocks and hp > 80: return 'Heavy-Duty Boots'
    if speed >= 110 and (attack >= 120 or sp_attack >= 120):
        return random.choice(['Life Orb', 'Choice Specs' if sp_attack > attack else 'Choice Band'])
    elif speed >= 80 and (attack >= 100 or sp_attack >= 100):
        return random.choice(['Choice Scarf', 'Expert Belt', 'Life Orb'])
    elif hp < 80 and (attack >= 130 or sp_attack >= 130):
        return 'Focus Sash'
    else:
        return 'Leftovers'

def analyze_team_weaknesses(team_types: dict) -> dict:
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
    for pokemon_types in team_types.values():
        for ptype in pokemon_types:
            if ptype in type_chart:
                for weakness_type, multiplier in type_chart[ptype].items():
                    weakness_count[weakness_type] = weakness_count.get(weakness_type, 0) + 1
    return {
        'critical': {t: count for t, count in weakness_count.items() if count >= 3},
        'moderate': {t: count for t, count in weakness_count.items() if count == 2},
        'all': weakness_count
    }

def calculate_evs(stats: dict, role: str) -> dict:
    if not stats: return {}
    attack = stats.get('attack', 0)
    sp_attack = stats.get('special-attack', 0)
    speed = stats.get('speed', 0)
    defense = stats.get('defense', 0)
    sp_defense = stats.get('special-defense', 0)
    is_physical = attack > sp_attack
    is_fast = speed >= 100
    if is_physical and is_fast: return {'HP': 0, 'Atk': 252, 'Def': 4, 'SpA': 0, 'SpD': 0, 'Spe': 252}
    elif is_physical and not is_fast: return {'HP': 252, 'Atk': 252, 'Def': 4, 'SpA': 0, 'SpD': 0, 'Spe': 0}
    elif not is_physical and is_fast: return {'HP': 0, 'Atk': 0, 'Def': 0, 'SpA': 252, 'SpD': 4, 'Spe': 252}
    elif not is_physical and not is_fast: return {'HP': 252, 'Atk': 0, 'Def': 0, 'SpA': 252, 'SpD': 4, 'Spe': 0}
    if defense > sp_defense: return {'HP': 252, 'Atk': 0, 'Def': 252, 'SpA': 0, 'SpD': 4, 'Spe': 0}
    else: return {'HP': 252, 'Atk': 0, 'Def': 4, 'SpA': 0, 'SpD': 252, 'Spe': 0}

def fetch_pokemon_data(pokemon_name: str, archetype_data: dict, original_name: Optional[str] = None):
    try:
        identifier = normalize_pokemon_identifier(pokemon_name)
        url = f"https://pokeapi.co/api/v2/pokemon/{identifier}"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())

        species_url = data['species']['url']
        with urllib.request.urlopen(species_url, timeout=5) as response:
            species_data = json.loads(response.read().decode())
            
        time.sleep(0.5)
        sprites = data['sprites']
        sprite_url = None
        if sprites.get('versions', {}).get('generation-v', {}).get('black-white', {}).get('animated', {}).get('front_default'):
            sprite_url = sprites['versions']['generation-v']['black-white']['animated']['front_default']
        elif sprites.get('other', {}).get('showdown', {}).get('front_default'):
            sprite_url = sprites['other']['showdown']['front_default']
        elif sprites.get('front_default'):
            sprite_url = sprites['front_default']
        
        pokemon_types = [t['type']['name'] for t in data['types']]
        stats = {s['stat']['name']: s['base_stat'] for s in data['stats']}
        
        # Apply Genetics (GitHub Stats)
        if github_stats:
            genetics = github_stats.GitHubGenetics.get_stats()
            stats = github_stats.GitHubGenetics.apply_genetics(stats, genetics)
        
        signature_moves = select_signature_moves(data['moves'], pokemon_types, stats, original_name or data['name'])
        all_abilities = [a['ability']['name'].replace('-', ' ').title() for a in data['abilities']]
        best_ability = select_competitive_ability(original_name or data['name'], all_abilities)
        competitive_nature = select_competitive_nature(stats)
        
        if stats:
            top_stat_key = max(stats, key=stats.get)
            role = ROLE_BY_STAT.get(top_stat_key, 'Balanced Command Core')
        else:
            role = 'Balanced Command Core'

        competitive_item = select_competitive_item(stats, role, original_name or data['name'], pokemon_types, archetype_data)
        ev_spread = calculate_evs(stats, role)

        # Generate SVG
        if svg_generator:
            svg_generator.generate_radar_chart(stats, original_name or data['name'])

        return {
            'name': (original_name or data['name']).title(),
            'types': pokemon_types,
            'height': data['height'] / 10,
            'weight': data['weight'] / 10,
            'stats': stats,
            'abilities': all_abilities,
            'best_ability': best_ability,
            'nature': competitive_nature,
            'item': competitive_item,
            'evs': ev_spread,
            'signature_moves': signature_moves,
            'flavor_text': get_english_flavor_text(species_data),
            'sprite': sprite_url,
            'shiny_sprite': sprites.get('front_shiny'),
            'id': data['id']
        }
    except Exception as e:
        print(f"Warning: Could not fetch data for {pokemon_name}: {e}")
        return None

def get_english_flavor_text(species_data):
    for entry in species_data.get('flavor_text_entries', []):
        if entry['language']['name'] == 'en':
            return entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
    return "A mysterious Pokémon that loves to code!"

def create_stat_bar(value, max_value=255):
    value = max(value, 0)
    filled = int((value / max_value) * 20)
    filled = max(0, min(20, filled))
    return '[' + '█' * filled + '░' * (20 - filled) + ']'

def create_power_gauge(value, max_value=1530, length=30):
    value = max(value, 0)
    ratio = min(value / max_value, 1) if max_value else 0
    filled = int(ratio * length)
    filled = max(0, min(length, filled))
    bar = '[' + '█' * filled + '░' * (length - filled) + ']'
    return f"{bar} {ratio * 100:5.1f}% capacity"

def create_flux_meter(value, max_value, length=18):
    if max_value <= 0: return '[' + '░' * length + '] 0% · STANDBY'
    value = max(value, 0)
    ratio = min(value / max_value, 1)
    filled = int(round(ratio * length))
    filled = max(0, min(length, filled))
    bar = '[' + '▓' * filled + '░' * (length - filled) + ']'
    if ratio >= 0.9: mode = "Ω-OVERDRIVE"
    elif ratio >= 0.7: mode = "VORTEX"
    elif ratio >= 0.5: mode = "CRUISE"
    elif ratio > 0: mode = "WARMUP"
    else: mode = "STANDBY"
    return f"{bar} {ratio * 100:4.0f}% · {mode}"

def get_pokemon_sprite_html(sprite_url, name, size=150):
    if sprite_url:
        return f'<img src="{sprite_url}" alt="{name}" width="{size}" height="{size}"/>'
    return f"```\n{POKEMON_ASCII_ART['default']}\n```"

def get_type_emoji(type_name):
    return TYPE_EMOJIS.get(type_name, "⚪")

def pick_index(n: int, day_seed: int) -> int:
    if n == 0: return 0
    return day_seed % n

def roll_random_encounter():
    # Use pity system if available
    if shiny_hunt:
        chance, pity_count = shiny_hunt.get_shiny_odds()
    else:
        chance = SHINY_TRIGGER_RATE
        pity_count = 0

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

    # Roll for shiny
    is_shiny = random.random() < chance

    if shiny_hunt:
        shiny_hunt.record_encounter(is_shiny)

    if is_shiny: callout += f" ✨ Shiny trigger tripped! (Odds: {chance:.1%})"

    return species, rarity, callout, is_shiny, pity_count

def describe_target(is_shiny: bool, legendary_mode: bool) -> str:
    if is_shiny: return "shimmering anomaly"
    if legendary_mode: return "legendary beacon"
    return "wild signal"

def generate_branching_paths(species: str, pokemon_info: Optional[dict], is_shiny: bool, legendary_mode: bool) -> str:
    display_name = species.title()
    type_summary = " / ".join([t.title() for t in pokemon_info["types"]]) if pokemon_info else "Unknown"
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

        body_lines = [
            f"  - **Battlefield State:** {description}",
            f"  - **Encounter Twist:** {twist}",
            f"  - **Command Brief:** Track the {legend_tag} target — {display_name} ({target_descriptor}{shiny_suffix}).",
            f"  - **Type Intel:** {type_summary}"
        ]

        def render_tactic(tactic: dict, odds: int) -> str:
            return (
                "  <details>\n"
                f"    <summary>{tactic['icon']} {tactic['title']} · {odds}% odds</summary>\n\n"
                f"    - **If it lands:** {tactic['success'].format(target=target_descriptor, pokemon=display_name)}\n"
                f"    - **If it whiffs:** {tactic['fallback'].format(pokemon=display_name)}\n"
                "  </details>"
            )

        tactics_block = "\n".join([render_tactic(tactic_left, odds_left), render_tactic(tactic_right, odds_right)])
        path_block = f"<details>\n  <summary>{emoji} Path {idx} — {title}</summary>\n\n" + "\n".join(body_lines) + "\n\n" + tactics_block + "\n</details>"
        path_blocks.append(path_block)

    return "\n\n".join(path_blocks)

# ==========================================
# MAIN EXECUTION
# ==========================================

# Load archetypes
with open(os.path.join(root, "data", "archetypes.json")) as f:
    arc = json.load(f)

now_utc = datetime.datetime.now(datetime.UTC)
day_number = now_utc.date().toordinal()
idx = pick_index(len(arc), day_number)
chosen = arc[idx]

random.seed(f"{day_number}-{chosen.get('id', idx)}")

print(f"🎯 Building README for archetype: {chosen['title']}")

# Fetch Pokémon data
print("\n🔍 Fetching Pokémon data from PokéAPI...")
pokemon_data = {}
team_list_data = [] # Store data for features
for pokemon_name in chosen['team']:
    print(f"  📡 Fetching {pokemon_name}...")
    data = fetch_pokemon_data(pokemon_name, chosen, original_name=pokemon_name)
    if data:
        pokemon_data[pokemon_name] = data
        team_list_data.append(data)
    else:
        # Fallback
        fallback = {
            'name': pokemon_name,
            'types': ['normal'],
            'height': 1.0, 'weight': 10.0,
            'stats': {'hp': 100, 'attack': 100, 'defense': 100, 'special-attack': 100, 'special-defense': 100, 'speed': 100},
            'abilities': ['Unknown'],
            'signature_moves': [],
            'flavor_text': 'A mysterious Pokémon!',
            'sprite': None, 'shiny_sprite': None, 'id': 0,
            'item': 'Leftovers', 'best_ability': 'Unknown', 'nature': 'Serious', 'evs': {}
        }
        pokemon_data[pokemon_name] = fallback
        team_list_data.append(fallback)

# Advanced Features Generation
weather = WeatherSystem.get_daily_weather(day_number)
quest = QuestGenerator.get_daily_quest(day_number)
pokepaste_link = PokePasteGenerator.generate_paste(team_list_data)
battle_log = BattleSimulator.simulate_battle(chosen['title'], "Blue", chosen['lead'])

# Random Encounter
random_choice, encounter_rarity, encounter_callout, encounter_is_shiny, pity_val = roll_random_encounter()
print(f"\n✨ Random encounter: {random_choice.title()} [{encounter_rarity}] (Pity: {pity_val})")
random_pokemon_data = fetch_pokemon_data(random_choice, {}, original_name=random_choice)
branching_paths_block = generate_branching_paths(
    random_choice, random_pokemon_data, encounter_is_shiny, encounter_rarity == "Legendary Sighting"
)

# Generate Team Banner
banner_path = "assets/team_banner.png"
if image_compositor:
    banner_path = image_compositor.generate_team_banner(team_list_data, weather['name'])

# Load template
with open(os.path.join(root, "README.template.md")) as f:
    template = f.read()

# Build Team Data
lead_name = chosen['lead']
lead_data = pokemon_data.get(lead_name, {})
lead_stats = lead_data.get('stats', {})

team_type_counts = {}
team_types_by_pokemon = {}
team_dossiers = []
total_speed = 0
team_bst_total = 0
fastest_member = (None, 0)
heaviest_member = (None, 0)
bst_member = (None, 0)

for pokemon_name in chosen['team']:
    pdata = pokemon_data.get(pokemon_name, {})
    stats = pdata.get('stats', {})
    types = pdata.get('types', ['normal'])

    team_types_by_pokemon[pokemon_name] = types
    for t in types: team_type_counts[t] = team_type_counts.get(t, 0) + 1

    speed_value = stats.get('speed', 0)
    total_speed += speed_value
    if speed_value > fastest_member[1]: fastest_member = (pokemon_name, speed_value)

    weight = pdata.get('weight', 0)
    if weight > heaviest_member[1]: heaviest_member = (pokemon_name, weight)

    bst = sum(stats.values()) if stats else 0
    team_bst_total += bst
    if bst > bst_member[1]: bst_member = (pokemon_name, bst)

    formatted_moves = []
    for move in pdata.get('signature_moves', []):
        emoji = get_type_emoji(move.get('type', 'normal'))
        power_text = f"{move.get('power')} BP" if move.get('power') else "Utility"
        formatted_moves.append(f"  - {emoji} {move.get('name')} · {move.get('damage_class').title()} · {power_text}")
    move_lines = "\n".join(formatted_moves) or "  - (pending scouting)"

    ev_parts = [f"{v} {k}" for k, v in pdata.get('evs', {}).items() if v > 0]
    ev_text = " / ".join(ev_parts) if ev_parts else "0 / 0 / 0 / 0 / 0 / 0"
    
    top_stat_key = max(stats, key=stats.get) if stats else 'hp'
    top_stat_val = stats.get(top_stat_key, 0)
    
    # Use the generated SVG URL if available (relative path)
    stat_radar = f"assets/stats_{normalize_pokemon_identifier(pokemon_name)}.svg"

    dossier = (
        f"<details open>\n"
        f"<summary>⚔️ <strong>{pokemon_name}</strong> · "
        + " / ".join([get_type_emoji(t) + t.upper() for t in types])
        + "</summary>\n\n"
        f"<div align=\"center\">\n{get_pokemon_sprite_html(pdata.get('sprite'), pokemon_name, 160)}\n"
        f"<br/><img src=\"{stat_radar}\" width=\"200\" height=\"200\" alt=\"Stats Radar\"/>\n</div>\n\n"
        f"- **Base Stat Total:** {bst}\n"
        f"- **Top Stat:** {top_stat_key.title()} ({top_stat_val})\n"
        f"- **Battle Role:** {pdata.get('role', 'Unknown')}\n"
        f"- **Ability:** {pdata.get('best_ability', 'Unknown')}\n"
        f"- **Nature:** {pdata.get('nature', 'Serious')}\n"
        f"- **Held Item:** {pdata.get('item', 'Leftovers')}\n"
        f"- **EV Spread:** {ev_text}\n"
        f"- **Signature Moves:**\n{move_lines}\n"
        f"</details>"
    )
    team_dossiers.append(dossier)

# Coach Advice
coach_advice = "Coach is out to lunch."
if coach_ai:
    coach_advice = coach_ai.analyze_matchup(team_list_data)

# Replacements Dictionary
replacements = {
    '{CURRENT_DATE}': now_utc.strftime("%Y-%m-%d %H:%M UTC"),
    '{DAY_NUMBER}': str(day_number),
    '{POKEDEX_COUNT}': str(len(pokemon_data)),
    '{ARCHETYPE_TITLE}': chosen['title'],
    '{ARCHETYPE_EMOJI}': get_type_emoji(lead_data.get('types', ['normal'])[0]),
    '{LEAD_POKEMON}': lead_name,
    '{LEAD_EMOJI}': get_type_emoji(lead_data.get('types', ['normal'])[0]),
    '{LEAD_ASCII}': get_pokemon_sprite_html(lead_data.get('sprite'), lead_name, 200),
    '{LEAD_TYPES}': ' '.join([get_type_emoji(t) + t.upper() for t in lead_data.get('types', ['normal'])]),
    '{LEAD_ABILITY}': lead_data.get('best_ability', 'Unknown'),
    '{LEAD_NATURE}': lead_data.get('nature', 'Serious'),
    '{LEAD_ITEM}': lead_data.get('item', 'Leftovers'),
    '{LEAD_EVS}': ' / '.join([f"{v} {k}" for k, v in lead_data.get('evs', {}).items() if v > 0]),
    '{LEAD_HEIGHT}': f"{lead_data.get('height', 1.0):.1f}m",
    '{LEAD_WEIGHT}': f"{lead_data.get('weight', 10.0):.1f}kg",
    '{LEAD_HP}': str(lead_stats.get('hp', 0)),
    '{LEAD_ATK}': str(lead_stats.get('attack', 0)),
    '{LEAD_DEF}': str(lead_stats.get('defense', 0)),
    '{LEAD_SPATK}': str(lead_stats.get('special-attack', 0)),
    '{LEAD_SPDEF}': str(lead_stats.get('special-defense', 0)),
    '{LEAD_SPEED}': str(lead_stats.get('speed', 0)),
    '{LEAD_HP_BAR}': create_stat_bar(lead_stats.get('hp', 0)),
    '{LEAD_ATK_BAR}': create_stat_bar(lead_stats.get('attack', 0)),
    '{LEAD_DEF_BAR}': create_stat_bar(lead_stats.get('defense', 0)),
    '{LEAD_SPATK_BAR}': create_stat_bar(lead_stats.get('special-attack', 0)),
    '{LEAD_SPDEF_BAR}': create_stat_bar(lead_stats.get('special-defense', 0)),
    '{LEAD_SPEED_BAR}': create_stat_bar(lead_stats.get('speed', 0)),
    '{TEAM_VISUAL}': f'<img src="{banner_path}" alt="Team Banner" width="100%">',
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
    '{TEAM_DETAIL_BLOCK}': '\n\n'.join(team_dossiers),
    '{BRANCHING_STORY_BLOCK}': branching_paths_block,
    '{WEATHER_EMOJI}': weather['emoji'],
    '{WEATHER_NAME}': weather['name'],
    '{WEATHER_EFFECT}': weather['effect'],
    '{QUEST_TEXT}': quest,
    '{BATTLE_LOG}': battle_log,
    '{POKEPASTE_LINK}': f"```\n{pokepaste_link}\n```",
    '{COACH_ADVICE}': coach_advice,
}

# Lead Moves
lead_moves_fmt = []
for move in lead_data.get('signature_moves', []):
    emoji = get_type_emoji(move.get('type', 'normal'))
    power = f"{move.get('power')} BP" if move.get('power') else "Utility"
    lead_moves_fmt.append(f"- **{move.get('name')}** · {emoji} {move.get('damage_class').title()} · {power}")
replacements['{LEAD_MOVES}'] = "\n".join(lead_moves_fmt) or "- Recon uplink pending..."

# Weakness Analysis
w_analysis = analyze_team_weaknesses(team_types_by_pokemon)
w_lines = []
if w_analysis['critical']:
    w_lines.append("### ⚠️ Critical Weaknesses (3+ Pokemon)")
    for wtype, count in sorted(w_analysis['critical'].items(), key=lambda x: -x[1]):
        w_lines.append(f"- {get_type_emoji(wtype)} **{wtype.upper()}** threatens {count} team members")
if w_analysis['moderate']:
    w_lines.append("\n### ⚡ Moderate Weaknesses (2 Pokemon)")
    for wtype, count in sorted(w_analysis['moderate'].items(), key=lambda x: -x[1]):
        w_lines.append(f"- {get_type_emoji(wtype)} **{wtype.upper()}** hits {count} team members")
if not w_lines: w_lines.append("✅ No critical type weaknesses detected.")
replacements['{WEAKNESS_ANALYSIS}'] = "\n".join(w_lines)

# Type Coverage
c_lines = [f"- {get_type_emoji(t)} **{t.upper()}** ×{c}" for t, c in sorted(team_type_counts.items(), key=lambda x: -x[1])]
replacements['{TYPE_COVERAGE_BLOCK}'] = "\n".join(c_lines)

# Misc Metrics
avg_speed = total_speed / len(chosen['team'])
replacements['{UNIQUE_TYPE_COUNT}'] = str(len(team_type_counts))
replacements['{AVERAGE_SPEED}'] = f"{avg_speed:.1f}"
replacements['{FASTEST_MEMBER}'] = fastest_member[0] or "Unknown"
replacements['{FASTEST_SPEED}'] = str(fastest_member[1])
replacements['{HEAVIEST_MEMBER}'] = heaviest_member[0] or "Unknown"
replacements['{HEAVIEST_WEIGHT}'] = f"{heaviest_member[1]:.1f}kg"
replacements['{HIGHEST_BST_MEMBER}'] = bst_member[0] or "Unknown"
replacements['{HIGHEST_BST}'] = str(bst_member[1])
replacements['{POWER_LEVEL}'] = str(team_bst_total)
replacements['{POWER_LEVEL_BAR}'] = create_power_gauge(team_bst_total, max(1, len(chosen['team'])) * 720)
replacements['{SYNERGY_METER}'] = create_flux_meter(len(team_type_counts), len(chosen['team']))
replacements['{SPEED_PULSE}'] = create_flux_meter(avg_speed, 180)
replacements['{BST_OVERDRIVE}'] = create_flux_meter(bst_member[1], 720)
replacements['{TEMPO_CALLSIGN}'] = "Adaptive cadence engaged." if avg_speed > 90 else "Glacial recon mode."
replacements['{HYPERSTREAM_BLOCK}'] = f"- **Synergy:** {len(team_type_counts)} types.\n- **Speed:** Avg {avg_speed:.1f}."
replacements['{BONKERS_TAGLINE}'] = "battle telemetry screaming through neon conduits"
replacements['{ANALYTICS_BLURB}'] = f"Squad average speed: {avg_speed:.1f}."
replacements['{LEAD_ROLE}'] = lead_data.get('role', 'Balanced Command Core')
replacements['{GENERATION}'] = str(random.randint(1, 9))
replacements['{API_CALLS}'] = str(len(pokemon_data) + 1)
replacements['{ACHIEVEMENT_DATE}'] = now_utc.strftime("%Y-%m-%d")

# Random Pokemon replacements
if random_pokemon_data:
    replacements['{RANDOM_POKEMON}'] = random_pokemon_data['name'].upper()
    replacements['{RANDOM_POKEMON_ASCII}'] = get_pokemon_sprite_html(random_pokemon_data.get('sprite'), random_pokemon_data['name'], 150)
    replacements['{RANDOM_POKEMON_TYPES}'] = ' '.join([get_type_emoji(t) + t.upper() for t in random_pokemon_data.get('types', ['normal'])])
    replacements['{RANDOM_POKEMON_HEIGHT}'] = f"{random_pokemon_data['height']:.1f}m"
    replacements['{RANDOM_POKEMON_WEIGHT}'] = f"{random_pokemon_data['weight']:.1f}kg"
    replacements['{RANDOM_POKEMON_ABILITIES}'] = ', '.join(random_pokemon_data['abilities'])
    replacements['{RANDOM_POKEMON_FLAVOR}'] = random_pokemon_data['flavor_text']
else:
    replacements['{RANDOM_POKEMON}'] = 'MISSINGNO'
    replacements['{RANDOM_POKEMON_ASCII}'] = '???'
    replacements['{RANDOM_POKEMON_TYPES}'] = 'GLITCH'
    replacements['{RANDOM_POKEMON_HEIGHT}'] = '???'
    replacements['{RANDOM_POKEMON_WEIGHT}'] = '???'
    replacements['{RANDOM_POKEMON_ABILITIES}'] = '???'
    replacements['{RANDOM_POKEMON_FLAVOR}'] = 'System Error'

replacements['{ENCOUNTER_SUMMARY}'] = f"🎲 Encounter: {random_choice.title()}"
replacements['{ENCOUNTER_RARITY}'] = encounter_rarity
replacements['{ENCOUNTER_SIGNAL}'] = encounter_callout
pity_display = f"(Days Dry: {pity_val})" if pity_val > 0 else "(Reset)"
replacements['{SHINY_TRIGGER_PANEL}'] = f"Shiny Hunt Status: {pity_display} - Odds: {(shiny_hunt.get_shiny_odds()[0] if shiny_hunt else 0):.1%}"

# Apply replacements
output = template
for key, value in replacements.items():
    output = output.replace(key, str(value))

# Update archetype section
output = re.sub(
    r"<!-- CURRENT_ARCHETYPE_START -->.*?<!-- CURRENT_ARCHETYPE_END -->",
    f"<!-- CURRENT_ARCHETYPE_START -->\n> **Rotation Profile:** {chosen['title']}\n> **Command Lead:** {lead_name}\n<!-- CURRENT_ARCHETYPE_END -->",
    output,
    flags=re.S
)

with open(os.path.join(root, "README.md"), "w") as f:
    f.write(output)

print("\n✅ README built successfully!")
