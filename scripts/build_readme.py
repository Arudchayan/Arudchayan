#!/usr/bin/env python3
import json
import os
import datetime
import random
import urllib.request
import time
from collections import Counter

import svg_generator
import github_metrics
import banner_generator
import coach

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
}

MOVE_CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "move_cache.json")

def load_move_cache():
    try:
        with open(MOVE_CACHE_FILE, 'r') as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}

MOVE_CACHE: dict[str, dict] = load_move_cache()

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

root = os.path.dirname(os.path.dirname(__file__))

# ==========================================
# ADVANCED GAME ENGINES
# ==========================================

WEATHER_TYPES = [
    {"name": "Clear Skies", "emoji": "☀️", "effect": "Standard battle conditions."},
    {"name": "Harsh Sunlight", "emoji": "🔥", "effect": "Fire moves boosted 50%, Water moves weakened 50%."},
    {"name": "Rain", "emoji": "🌧️", "effect": "Water moves boosted 50%, Fire moves weakened 50%."},
    {"name": "Sandstorm", "emoji": "🏜️", "effect": "Rock types get 50% Sp. Def boost. Chip damage active."},
    {"name": "Snow", "emoji": "❄️", "effect": "Ice types get 50% Def boost."},
]

QUESTS = [
    "Optimize 3 functions to increase Metagross's calculation speed.",
    "Push a commit before noon to outspeed Rival Weavile.",
    "Refactor legacy code to clear Gengar's Cursed Body status.",
    "Add unit tests to strengthen the team's Synergy Mesh.",
    "Review a PR to teach Alakazam 'Future Sight'.",
]

def ev_string(evs: dict) -> str:
    return " / ".join(f"{v} {k}" for k, v in evs.items() if v > 0)

def generate_paste(pokemon_list: list[dict]) -> str:
    paste_lines = []
    for p in pokemon_list:
        name = p['name']
        item = p['item']
        ability = p['best_ability']
        nature = p['nature']
        moves = [m['name'] for m in p['signature_moves']]

        block = f"{name} @ {item}\nAbility: {ability}\nEVs: {ev_string(p['evs'])}\n{nature} Nature"
        for m in moves:
            block += f"\n- {m}"
        paste_lines.append(block)

    return "\n\n".join(paste_lines)

def load_trainer_history():
    default = {"shiny_hunt": {"encounters_since_last": 0, "last_found": None}}
    history_path = os.path.join(root, "data", "trainer_history.json")
    if os.path.exists(history_path):
        with open(history_path) as f:
            loaded = json.load(f)
        loaded.setdefault("shiny_hunt", default["shiny_hunt"])
        return loaded
    return default
def normalize_pokemon_identifier(pokemon_name: str) -> str:
    lower_name = pokemon_name.lower().strip()
    if lower_name.startswith("mega "):
        suffix = lower_name.replace("mega ", "", 1)
        suffix = suffix.replace(" ", "-")
        return f"{suffix}-mega"
    return lower_name.replace(" ", "-")

def select_signature_moves(api_moves: list, pokemon_types: list[str], pokemon_stats: dict, pokemon_name: str) -> list[dict]:
    attack = pokemon_stats.get('attack', 0)
    is_physical = attack > pokemon_stats.get('special-attack', 0)

    candidates: list[dict] = []
    seen_moves: set[str] = set()
    for entry in api_moves:
        move_name = entry.get("move", {}).get("name")
        move_url = entry.get("move", {}).get("url")
        if not move_name or not move_url or move_name in seen_moves or move_name in BAD_MOVES:
            continue
        eligible_details = [
            detail for detail in entry.get("version_group_details", [])
            if detail.get("move_learn_method", {}).get("name") in MOVE_METHOD_PRIORITY
        ]
        if not eligible_details:
            continue
        seen_moves.add(move_name)
        best_detail = min(eligible_details, key=lambda detail: (
            VERSION_PRIORITY.index(detail.get("version_group", {}).get("name", ""))
            if detail.get("version_group", {}).get("name", "") in VERSION_PRIORITY
            else len(VERSION_PRIORITY),
            MOVE_METHOD_PRIORITY.get(detail.get("move_learn_method", {}).get("name", ""), 99),
            -detail.get("level_learned_at", 0),
        ))
        metadata = MOVE_CACHE.get(move_url, {})
        damage_class = metadata.get("damage_class", "status")
        power = metadata.get("power") or 0
        method = best_detail.get("move_learn_method", {}).get("name", "unknown")
        candidates.append({
            "name": move_name.replace("-", " ").title(),
            "raw_name": move_name,
            "type": metadata.get("type"),
            "power": power,
            "damage_class": damage_class,
            "key": (
                0 if move_name in COMPETITIVE_PRIORITY_MOVES else 1,
                0 if damage_class == "status" or (damage_class == "physical") == is_physical else 1,
                0 if metadata.get("type") in pokemon_types else 1,
                0 if damage_class == "status" else 1,
                MOVE_METHOD_PRIORITY.get(method, 99),
                -power,
                -best_detail.get("level_learned_at", 0),
                move_name.replace("-", " ").title(),
            ),
        })

    final_moves = sorted(candidates, key=lambda m: m.pop("key"))[:4]
    if 'rayquaza' in pokemon_name.lower():
        final_moves = [m for m in final_moves if m["raw_name"] != 'dragon-ascent'][:3]
        final_moves.insert(0, {
            "name": "Dragon Ascent", "raw_name": "dragon-ascent", "type": "flying",
            "power": 120, "damage_class": "physical",
        })

    return final_moves

def select_competitive_nature(stats: dict) -> str:
    if not stats: return 'Serious'
    attack = stats.get('attack', 0)
    sp_attack = stats.get('special-attack', 0)
    speed = stats.get('speed', 0)
    if attack > sp_attack: return 'Jolly' if speed >= 100 else 'Adamant'
    elif sp_attack > attack: return 'Timid' if speed >= 100 else 'Modest'
    else: return 'Hasty' if speed >= 100 else 'Mild'

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

def select_competitive_item(stats: dict, types: list[str]) -> str:
    if not stats: return 'Leftovers'
    attack = stats.get('attack', 0)
    sp_attack = stats.get('special-attack', 0)
    speed = stats.get('speed', 0)
    hp = stats.get('hp', 0)
    specs_or_band = 'Choice Specs' if sp_attack > attack else 'Choice Band'
    if any(t in ['fire', 'ice', 'flying', 'bug'] for t in types) and hp > 80:
        return 'Heavy-Duty Boots'
    if speed >= 110 and (attack >= 120 or sp_attack >= 120):
        return random.choice(['Life Orb', specs_or_band])
    elif speed >= 80 and (attack >= 100 or sp_attack >= 100):
        return random.choice(['Choice Scarf', 'Expert Belt', 'Life Orb'])
    elif hp < 80 and (attack >= 130 or sp_attack >= 130):
        return 'Focus Sash'
    else:
        return 'Leftovers'

def analyze_team_weaknesses(team_types: dict) -> dict:
    weakness_count = Counter(
        w
        for pokemon_types in team_types.values()
        for ptype in pokemon_types
        for w in coach.TYPE_CHART.get(ptype, [])
    )
    return {
        'critical': {t: count for t, count in weakness_count.items() if count >= 3},
        'moderate': {t: count for t, count in weakness_count.items() if count == 2},
    }

def calculate_evs(stats: dict) -> dict:
    if not stats: return {}
    attack = stats.get('attack', 0)
    sp_attack = stats.get('special-attack', 0)
    speed = stats.get('speed', 0)
    is_physical = attack > sp_attack
    is_fast = speed >= 100
    if is_physical and is_fast: return {'HP': 0, 'Atk': 252, 'Def': 4, 'SpA': 0, 'SpD': 0, 'Spe': 252}
    elif is_physical and not is_fast: return {'HP': 252, 'Atk': 252, 'Def': 4, 'SpA': 0, 'SpD': 0, 'Spe': 0}
    elif not is_physical and is_fast: return {'HP': 0, 'Atk': 0, 'Def': 0, 'SpA': 252, 'SpD': 4, 'Spe': 252}
    else: return {'HP': 252, 'Atk': 0, 'Def': 0, 'SpA': 252, 'SpD': 4, 'Spe': 0}

def fetch_pokemon_data(pokemon_name: str):
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
        
        signature_moves = select_signature_moves(data['moves'], pokemon_types, stats, pokemon_name)
        all_abilities = [a['ability']['name'].replace('-', ' ').title() for a in data['abilities']]
        best_ability = select_competitive_ability(pokemon_name, all_abilities)
        competitive_nature = select_competitive_nature(stats)

        competitive_item = select_competitive_item(stats, pokemon_types)
        ev_spread = calculate_evs(stats)

        # Generate SVG
        svg_generator.generate_radar_chart(stats, normalize_pokemon_identifier(pokemon_name))

        return {
            'name': pokemon_name.title(),
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
            'sprite': sprite_url
        }
    except Exception as e:
        print(f"Warning: Could not fetch data for {pokemon_name}: {e}")
        return None

def get_english_flavor_text(species_data):
    for entry in species_data.get('flavor_text_entries', []):
        if entry['language']['name'] == 'en':
            return entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
    return "A mysterious Pokémon that loves to code!"

def format_move(move: dict) -> str:
    emoji = get_type_emoji(move.get('type', 'normal'))
    power = f"{move.get('power')} BP" if move.get('power') else "Utility"
    return f"{emoji} {move.get('name')} · {move.get('damage_class').title()} · {power}"

def bar(value, max_value, length=20, filled_char='█', suffix=""):
    filled = int(min(max(value, 0) / max_value, 1) * length) if max_value > 0 else 0
    return '[' + filled_char * filled + '░' * (length - filled) + ']' + suffix

def flux_suffix(pct: float) -> str:
    mode = ("Ω-OVERDRIVE" if pct >= 0.9 else "VORTEX" if pct >= 0.7
            else "CRUISE" if pct >= 0.5 else "WARMUP" if pct > 0 else "STANDBY")
    return f" {pct * 100:4.0f}% · {mode}"

def get_pokemon_sprite_html(sprite_url, name, size=150):
    if sprite_url:
        return f'<img src="{sprite_url}" alt="{name}" width="{size}" height="{size}"/>'
    return '???'

def get_type_emoji(type_name):
    return TYPE_EMOJIS.get(type_name, "⚪")

def roll_random_encounter():
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

    is_shiny = random.random() < SHINY_TRIGGER_RATE
    if is_shiny: callout += " ✨ Shiny trigger tripped!"

    return species, rarity, callout, is_shiny

def generate_branching_paths(species: str, pokemon_info: dict, is_shiny: bool, legendary_mode: bool) -> str:
    display_name = species.title()
    type_summary = " / ".join([t.title() for t in pokemon_info["types"]]) if pokemon_info else "Unknown"
    target_descriptor = "shimmering anomaly" if is_shiny else "legendary beacon" if legendary_mode else "wild signal"
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

        tactics_block = "\n".join(
            "  <details>\n"
            f"    <summary>{tactic['icon']} {tactic['title']} · {odds}% odds</summary>\n\n"
            f"    - **If it lands:** {tactic['success'].format(target=target_descriptor, pokemon=display_name)}\n"
            f"    - **If it whiffs:** {tactic['fallback'].format(pokemon=display_name)}\n"
            "  </details>"
            for tactic, odds in ((tactic_left, odds_left), (tactic_right, odds_right))
        )
        path_block = f"<details>\n  <summary>{emoji} Path {idx} — {title}</summary>\n\n" + "\n".join(body_lines) + "\n\n" + tactics_block + "\n</details>"
        path_blocks.append(path_block)

    return "\n\n".join(path_blocks)

# ==========================================
# MAIN EXECUTION
# ==========================================

# Load archetypes
with open(os.path.join(root, "data", "archetypes.json")) as f:
    arc = json.load(f)

# === 2. FETCH GENETICS STATS ===
genetics_data = github_metrics.get_github_stats()
genetics_bonuses = github_metrics.calculate_genetic_bonuses(genetics_data)
print(f"🧬 Genetics Loaded: {genetics_bonuses.get('desc')}")

now_utc = datetime.datetime.now(datetime.UTC)
day_number = now_utc.date().toordinal()
idx = day_number % len(arc)
chosen = arc[idx]

random.seed(f"{day_number}-{chosen['id']}")
weather = random.choice(WEATHER_TYPES)
quest = random.choice(QUESTS)

print(f"🎯 Building README for archetype: {chosen['title']}")

# Fetch Pokémon data
print("\n🔍 Fetching Pokémon data from PokéAPI...")
pokemon_data = {}

for pokemon_name in chosen['team']:
    print(f"  📡 Fetching {pokemon_name}...")
    data = fetch_pokemon_data(pokemon_name)
    if not data:
        # Fallback
        data = {
            'name': pokemon_name,
            'types': ['normal'],
            'height': 1.0, 'weight': 10.0,
            'stats': {'hp': 100, 'attack': 100, 'defense': 100, 'special-attack': 100, 'special-defense': 100, 'speed': 100},
            'abilities': ['Unknown'],
            'signature_moves': [],
            'flavor_text': 'A mysterious Pokémon!',
            'sprite': None,
            'item': 'Leftovers', 'best_ability': 'Unknown', 'nature': 'Serious', 'evs': {}
        }
    pokemon_data[pokemon_name] = data

# Advanced Features Generation
team_list_data = list(pokemon_data.values())
sprite_urls = [d.get('sprite') for d in team_list_data]
pokepaste_link = generate_paste(team_list_data)
battle_log = (
    f"⚔️ **Battle Start!** Trainer {chosen['title']} vs Rival Blue!\n"
    f"🔹 **Turn 1:** {chosen['lead']} Mega Evolves and uses **Dragon Ascent**!\n"
    "🔸 Rival's Garchomp survives on Focus Sash and uses **Swords Dance**!\n"
    f"🔹 **Turn 2:** {chosen['lead']} uses **Extreme Speed** for the KO!\n"
    "🔸 Rival sends out Tapu Koko. Electric Terrain activates!\n"
    f"🔹 **Turn 3:** {chosen['lead']} switches to Landorus-T to Intimidate!\n"
    f"🏆 **Result:** Rival forfeits! **{chosen['title']} Wins!**"
)

# === 4. BANNER GENERATION ===
print("🖼️ Generating Team Banner...")
banner_generator.generate_team_banner(sprite_urls, weather['name'])

# === 5. SHINY HUNT LOGIC ===
trainer_history = load_trainer_history()
shiny_hunt = trainer_history["shiny_hunt"]

random_choice, encounter_rarity, encounter_callout, encounter_is_shiny = roll_random_encounter()

# Update History
if encounter_is_shiny:
    shiny_hunt["encounters_since_last"] = 0
    shiny_hunt["last_found"] = now_utc.strftime("%Y-%m-%d")
    print("✨ SHINY FOUND! Resetting counter.")
else:
    shiny_hunt["encounters_since_last"] += 1

with open(os.path.join(root, "data", "trainer_history.json"), "w") as f:
    json.dump(trainer_history, f, indent=2)

print(f"\n✨ Random encounter: {random_choice.title()} [{encounter_rarity}]")
random_pokemon_data = fetch_pokemon_data(random_choice)
branching_paths_block = generate_branching_paths(
    random_choice, random_pokemon_data, encounter_is_shiny, encounter_rarity == "Legendary Sighting"
)

# === 6. GYM LEADER CHALLENGERS ===
challenger_text = "No recent challengers recorded."
challenger_path = os.path.join(root, "data", "challengers.json")
if os.path.exists(challenger_path):
    with open(challenger_path) as f:
        challengers = json.load(f)
        if challengers:
            rows = ["| Date | Challenger | Team | Result |", "| --- | --- | --- | --- |"]
            for c in challengers[:5]: # Top 5
                rows.append(f"| {c['date']} | {c['challenger']} | {', '.join(c['team'])} | {c['result']} ({c['winner']}) |")
            challenger_text = "\n".join(rows)

# Load template
with open(os.path.join(root, "README.template.md")) as f:
    template = f.read()

# Build Team Data
lead_name = chosen['lead']
lead_data = pokemon_data.get(lead_name, {})
lead_stats = lead_data.get('stats', {})

# === 7. APPLY GENETICS STATS TO LEAD ===
if lead_stats:
    lead_stats['attack'] += genetics_bonuses['attack_bonus']
    lead_stats['defense'] += genetics_bonuses['defense_bonus']
    lead_stats['special-defense'] += genetics_bonuses['sp_def_bonus']

team_type_counts = {}
team_types_by_pokemon = {}
team_dossiers = []
total_speed = 0
team_bst_total = 0
max_bst = 0

for pokemon_name in chosen['team']:
    pdata = pokemon_data.get(pokemon_name, {})
    stats = pdata.get('stats', {})
    types = pdata.get('types', ['normal'])

    team_types_by_pokemon[pokemon_name] = types
    for t in types: team_type_counts[t] = team_type_counts.get(t, 0) + 1

    total_speed += stats.get('speed', 0)

    bst = sum(stats.values()) if stats else 0
    team_bst_total += bst
    max_bst = max(max_bst, bst)

    move_lines = "\n".join(f"  - {format_move(m)}" for m in pdata.get('signature_moves', [])) or "  - (pending scouting)"

    ev_text = ev_string(pdata.get('evs', {})) or "0 / 0 / 0 / 0 / 0 / 0"
    
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
        f"- **Ability:** {pdata.get('best_ability', 'Unknown')}\n"
        f"- **Nature:** {pdata.get('nature', 'Serious')}\n"
        f"- **Held Item:** {pdata.get('item', 'Leftovers')}\n"
        f"- **EV Spread:** {ev_text}\n"
        f"- **Signature Moves:**\n{move_lines}\n"
        f"</details>"
    )
    team_dossiers.append(dossier)

# === 8. COACH'S ADVICE ===
coach_tips = coach.get_coach_advice(
    lead_name,
    lead_data.get('types', ['normal']),
    lead_stats.get('speed', 90)
)

# Replacements Dictionary
replacements = {
    '{CURRENT_DATE}': now_utc.strftime("%Y-%m-%d %H:%M UTC"),
    '{DAY_NUMBER}': str(day_number),
    '{ARCHETYPE_TITLE}': chosen['title'],
    '{LEAD_POKEMON}': lead_name,
    '{LEAD_TYPES}': ' '.join([get_type_emoji(t) + t.upper() for t in lead_data.get('types', ['normal'])]),
    '{LEAD_ABILITY}': lead_data.get('best_ability', 'Unknown'),
    '{LEAD_NATURE}': lead_data.get('nature', 'Serious'),
    '{LEAD_ITEM}': lead_data.get('item', 'Leftovers'),
    '{LEAD_EVS}': ev_string(lead_data.get('evs', {})),
    '{LEAD_HEIGHT}': f"{lead_data.get('height', 1.0):.1f}m",
    '{LEAD_WEIGHT}': f"{lead_data.get('weight', 10.0):.1f}kg",
    '{LEAD_HP}': str(lead_stats.get('hp', 0)),
    '{LEAD_ATK}': str(lead_stats.get('attack', 0)),
    '{LEAD_DEF}': str(lead_stats.get('defense', 0)),
    '{LEAD_SPATK}': str(lead_stats.get('special-attack', 0)),
    '{LEAD_SPDEF}': str(lead_stats.get('special-defense', 0)),
    '{LEAD_SPEED}': str(lead_stats.get('speed', 0)),
    '{LEAD_HP_BAR}': bar(lead_stats.get('hp', 0), 255),
    '{LEAD_ATK_BAR}': bar(lead_stats.get('attack', 0), 255),
    '{LEAD_DEF_BAR}': bar(lead_stats.get('defense', 0), 255),
    '{LEAD_SPATK_BAR}': bar(lead_stats.get('special-attack', 0), 255),
    '{LEAD_SPDEF_BAR}': bar(lead_stats.get('special-defense', 0), 255),
    '{LEAD_SPEED_BAR}': bar(lead_stats.get('speed', 0), 255),
    '{TEAM_LIST}': ', '.join(chosen['team']),
    '{MEGA_INFO}': f"◆ {chosen['mega']} 💎" if chosen.get('mega') else '—',
    '{ZMOVE_INFO}': f"▲ {chosen['z_move']} ⚡" if chosen.get('z_move') else '—',
    '{TERA_INFO}': f"◇ {chosen['tera_type']} ✨" if chosen.get('tera_type') else '—',
    '{TEAM_DETAIL_BLOCK}': '\n\n'.join(team_dossiers),
    '{BRANCHING_STORY_BLOCK}': branching_paths_block,
    '{WEATHER_EMOJI}': weather['emoji'],
    '{WEATHER_NAME}': weather['name'],
    '{WEATHER_EFFECT}': weather['effect'],
    '{QUEST_TEXT}': quest,
    '{BATTLE_LOG}': battle_log,
    '{POKEPASTE_LINK}': f"```\n{pokepaste_link}\n```",
    '{GENETICS_LEVEL}': genetics_bonuses.get('level', '??'),
    '{GENETICS_BONUS_DESC}': genetics_bonuses.get('desc', ''),
    '{COACH_TIPS}': coach_tips,
    '{CHALLENGER_LIST}': challenger_text,
    '{SHINY_HUNT_STATUS}': f"Current Hunt: **{days_dry}** Days Dry. Odds: **{SHINY_TRIGGER_RATE*100:.2f}**",
}

# Lead Moves
lead_moves_fmt = [f"- **{format_move(m)}**" for m in lead_data.get('signature_moves', [])]
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
replacements['{POWER_LEVEL}'] = str(team_bst_total)
replacements['{POWER_LEVEL_BAR}'] = bar(team_bst_total, max(1, len(chosen['team'])) * 720, 30, suffix=f" {min(team_bst_total / (max(1, len(chosen['team'])) * 720), 1) * 100:5.1f}% capacity")
replacements['{SYNERGY_METER}'] = bar(len(team_type_counts), len(chosen['team']), 18, '▓', flux_suffix(min(len(team_type_counts) / len(chosen['team']), 1)))
replacements['{SPEED_PULSE}'] = bar(avg_speed, 180, 18, '▓', flux_suffix(min(avg_speed / 180, 1)))
replacements['{BST_OVERDRIVE}'] = bar(max_bst, 720, 18, '▓', flux_suffix(min(max_bst / 720, 1)))
replacements['{TEMPO_CALLSIGN}'] = "Adaptive cadence engaged." if avg_speed > 90 else "Glacial recon mode."

# Random Pokemon replacements
if random_pokemon_data:
    replacements['{RANDOM_POKEMON_ASCII}'] = get_pokemon_sprite_html(random_pokemon_data.get('sprite'), random_pokemon_data['name'], 150)
    replacements['{RANDOM_POKEMON_TYPES}'] = ' '.join([get_type_emoji(t) + t.upper() for t in random_pokemon_data.get('types', ['normal'])])
    replacements['{RANDOM_POKEMON_HEIGHT}'] = f"{random_pokemon_data['height']:.1f}m"
    replacements['{RANDOM_POKEMON_WEIGHT}'] = f"{random_pokemon_data['weight']:.1f}kg"
    replacements['{RANDOM_POKEMON_ABILITIES}'] = ', '.join(random_pokemon_data['abilities'])
    replacements['{RANDOM_POKEMON_FLAVOR}'] = random_pokemon_data['flavor_text']
else:
    replacements['{RANDOM_POKEMON_ASCII}'] = '???'
    replacements['{RANDOM_POKEMON_TYPES}'] = 'GLITCH'
    replacements['{RANDOM_POKEMON_HEIGHT}'] = '???'
    replacements['{RANDOM_POKEMON_WEIGHT}'] = '???'
    replacements['{RANDOM_POKEMON_ABILITIES}'] = '???'
    replacements['{RANDOM_POKEMON_FLAVOR}'] = 'System Error'

replacements['{ENCOUNTER_SUMMARY}'] = f"🎲 Encounter: {random_choice.title()}"
replacements['{ENCOUNTER_RARITY}'] = encounter_rarity
replacements['{ENCOUNTER_SIGNAL}'] = encounter_callout

# Apply replacements
output = template
for key, value in replacements.items():
    output = output.replace(key, str(value))

with open(os.path.join(root, "README.md"), "w") as f:
    f.write(output)

print("\n✅ README built successfully!")

