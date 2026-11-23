<p align="center"><img src="assets/hero.svg?v=739943" width="880" alt="Arudchayan · BattleOps Command Center"/></p>

<p align="center"><sub>Pokémon trainer by night · research engineer by day · open to ML research engineering roles where rigorous evaluation matters</sub></p>

<p align="center"><sub><strong>Now:</strong> evaluation harnesses for small LMs · monitorability &amp; agent safety · local-first AI tooling</sub></p>

## 🧠 AI Research & Evaluation

I build systems that check whether the check works: monitorability evals, agent safety gates, and reproducible evaluation harnesses.

| Project | What it is | Headline |
| --- | --- | --- |
| **[Turnwave](https://github.com/Arudchayan/Turnwave)**<br/><sub><code>Python</code> · <code>speech-to-speech</code> · <code>evals</code> · public</sub> | Local speech-to-speech research on LFM2.5-Audio-1.5B: streaming audio, interruption handling, Silero VAD, and a replayable eval harness. | Final-block playback race: **0/2,003 → 2,003/2,003** samples played, regression-tested. |
| **TraceScope**<br/><sub><code>Python</code> · <code>evals</code> · private R&amp;D</sub> | Small-LM safety-monitor evals: judge seed variance, prompt brittleness, and embedding-monitor transfer limits. | Reassuring summaries blind every monitor tested: detection **0.60 → 0.00** across keyword, embedding, and 0.5B-judge monitors. |
| **AgentGate**<br/><sub><code>Python</code> · <code>agent security</code> · private R&amp;D</sub> | Enforcement gate for agent file/email actions: allowlists, sensitive-pattern confirms, and measured block/legit rates. | **2/2** exfiltration tasks blocked and **14/14** boundary cases, with every bypass logged beside its fix. |
| **WarningTime**<br/><sub><code>Python</code> · <code>evals</code> · private R&amp;D</sub> | Trajectory-monitor metrics that separate detection from prevention. | Strict monitors false-alarm on **3/47** benign trajectories; lenient ones arrive up to **3 steps** late. |

<sub>Private R&amp;D write-ups are available on request — happy to walk through the harnesses and failure cases.</sub>

## 🛠️ Agent & Research Tooling

| Project | What it is | Headline |
| --- | --- | --- |
| **[adam-mcp](https://github.com/Arudchayan/adam-mcp)**<br/><sub><code>TypeScript</code> · <code>MCP</code> · <code>agents</code> · <a href="https://www.npmjs.com/package/adam-mcp">npm</a></sub> | Local-first, read-only MCP server for University of Basel ADAM. SWITCH edu-ID stays in the browser. | **npm 0.5.0** · 71 commits and 71 PRs in the last 30 days. |
| **[ResearchQuest](https://github.com/Arudchayan/ResearchQuest)**<br/><sub><code>React 19</code> · <code>Supabase</code> · <a href="https://rq.arudchayan.com">live demo</a></sub> | Scholarly workspace for papers, notes, ideas, a Today plan, Focus Studio, and DOI/Crossref import. | **Live demo** · realtime Supabase workspace. |

## 📦 Also Shipped

- **[overstay](https://github.com/Arudchayan/overstay)** `v0.2.1` — local-only time tracker and website limiter for Chrome, Edge, Brave, and Firefox.
- **[BASELCAL](https://baselcal.vercel.app)** — Uni Basel MSc Data Science planner with ECTS rules and ICS export.
- **[ResumeBuilder](https://github.com/Arudchayan/ResumeBuilder)** — one layout IR to vector PDF + DOCX, local-first.

---

## 🎮 Today's Trainer Card

<p align="center"><img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/807.gif" alt="Zeraora" width="72" height="72"/> <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/384.gif" alt="Rayquaza" width="72" height="72"/> <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/715.gif" alt="Noivern" width="72" height="72"/> <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/376.gif" alt="Metagross" width="72" height="72"/> <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/94.gif" alt="Gengar" width="72" height="72"/> <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/showdown/724.gif" alt="Decidueye" width="72" height="72"/></p>

**Day 739943** · Thunderborn Storm Raider · **Zeraora** lead · 🔥 Harsh Sunlight
**Roster:** Zeraora, Rayquaza, Noivern, Metagross, Gengar, Decidueye
**Quest:** Push a commit before noon to outspeed Rival Weavile.

<details>
<summary>⚔️ Open the full trainer card — squad dossiers, type intel, gym log</summary>

### Squad Dossiers

<details>
<summary>⚔️ <strong>Zeraora</strong> · ⚡ELECTRIC</summary>

<div align="center">
<img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/807.gif" alt="Zeraora" width="160" height="160"/>
<br/><img src="assets/stats_zeraora.svg?v=2" width="240" height="264" alt="Stats Radar"/>
</div>

- **Base Stat Total:** 600
- **Top Stat:** Speed (143)
- **Ability:** Volt Absorb
- **Nature:** Jolly
- **Held Item:** Expert Belt
- **EV Spread:** 252 Atk / 4 Def / 252 Spe
- **Signature Moves:**
  - ⚡ Thunder Wave · Status · Utility
  - 🥊 Bulk Up · Status · Utility
  - 🔮 Calm Mind · Status · Utility
  - ⚪ Protect · Status · Utility
</details>

<details>
<summary>⚔️ <strong>Rayquaza</strong> · 🐉DRAGON / 🕊️FLYING</summary>

<div align="center">
<img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/384.gif" alt="Rayquaza" width="160" height="160"/>
<br/><img src="assets/stats_rayquaza.svg?v=2" width="240" height="264" alt="Stats Radar"/>
</div>

- **Base Stat Total:** 680
- **Top Stat:** Attack (150)
- **Ability:** Air Lock
- **Nature:** Mild
- **Held Item:** Heavy-Duty Boots
- **EV Spread:** 252 HP / 252 SpA / 4 SpD
- **Signature Moves:**
  - 🕊️ Dragon Ascent · Physical · 120 BP
  - 🐉 Dragon Dance · Status · Utility
  - 🕊️ Defog · Status · Utility
  - 🕊️ Hurricane · Special · 110 BP
</details>

<details>
<summary>⚔️ <strong>Noivern</strong> · 🕊️FLYING / 🐉DRAGON</summary>

<div align="center">
<img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/715.gif" alt="Noivern" width="160" height="160"/>
<br/><img src="assets/stats_noivern.svg?v=2" width="240" height="264" alt="Stats Radar"/>
</div>

- **Base Stat Total:** 535
- **Top Stat:** Speed (123)
- **Ability:** Frisk
- **Nature:** Timid
- **Held Item:** Heavy-Duty Boots
- **EV Spread:** 252 SpA / 4 SpD / 252 Spe
- **Signature Moves:**
  - 🕊️ Roost · Status · Utility
  - 🕊️ Defog · Status · Utility
  - 🐉 Dragon Dance · Status · Utility
  - 🕊️ Hurricane · Special · 110 BP
</details>

<details>
<summary>⚔️ <strong>Metagross</strong> · ⚙️STEEL / 🔮PSYCHIC</summary>

<div align="center">
<img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/376.gif" alt="Metagross" width="160" height="160"/>
<br/><img src="assets/stats_metagross.svg?v=2" width="240" height="264" alt="Stats Radar"/>
</div>

- **Base Stat Total:** 600
- **Top Stat:** Attack (135)
- **Ability:** Clear Body
- **Nature:** Adamant
- **Held Item:** Leftovers
- **EV Spread:** 252 HP / 252 Atk / 4 Def
- **Signature Moves:**
  - ⚙️ Bullet Punch · Physical · 40 BP
  - ⚪ Protect · Status · Utility
  - 🪨 Stealth Rock · Status · Utility
  - ⚪ Substitute · Status · Utility
</details>

<details>
<summary>⚔️ <strong>Gengar</strong> · 👻GHOST / ☠️POISON</summary>

<div align="center">
<img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/94.gif" alt="Gengar" width="160" height="160"/>
<br/><img src="assets/stats_gengar.svg?v=2" width="240" height="264" alt="Stats Radar"/>
</div>

- **Base Stat Total:** 500
- **Top Stat:** Special-Attack (130)
- **Ability:** Cursed Body
- **Nature:** Timid
- **Held Item:** Life Orb
- **EV Spread:** 252 SpA / 4 SpD / 252 Spe
- **Signature Moves:**
  - ☠️ Toxic · Status · Utility
  - ☠️ Toxic Spikes · Status · Utility
  - 👻 Shadow Ball · Special · 80 BP
  - ☠️ Sludge Wave · Special · 95 BP
</details>

<details>
<summary>⚔️ <strong>Decidueye</strong> · 🌿GRASS / 👻GHOST</summary>

<div align="center">
<img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/showdown/724.gif" alt="Decidueye" width="160" height="160"/>
<br/><img src="assets/stats_decidueye.svg?v=2" width="240" height="264" alt="Stats Radar"/>
</div>

- **Base Stat Total:** 530
- **Top Stat:** Attack (107)
- **Ability:** Overgrow
- **Nature:** Adamant
- **Held Item:** Leftovers
- **EV Spread:** 252 HP / 252 Atk / 4 Def
- **Signature Moves:**
  - 🌿 Synthesis · Status · Utility
  - 👻 Shadow Sneak · Physical · 40 BP
  - 🌙 Nasty Plot · Status · Utility
  - 🕊️ Defog · Status · Utility
</details>

### Type Coverage & Defensive Analysis

- 🐉 **DRAGON** ×2
- 🕊️ **FLYING** ×2
- 👻 **GHOST** ×2
- ⚡ **ELECTRIC** ×1
- ⚙️ **STEEL** ×1
- 🔮 **PSYCHIC** ×1
- ☠️ **POISON** ×1
- 🌿 **GRASS** ×1

### ⚠️ Critical Weaknesses (3+ Pokemon)
- 🧊 **ICE** threatens 5 team members
- 🌍 **GROUND** threatens 3 team members
- 👻 **GHOST** threatens 3 team members
- 🌙 **DARK** threatens 3 team members

### ⚡ Moderate Weaknesses (2 Pokemon)
- 🐉 **DRAGON** hits 2 team members
- ✨ **FAIRY** hits 2 team members
- ⚡ **ELECTRIC** hits 2 team members
- 🪨 **ROCK** hits 2 team members
- 🔥 **FIRE** hits 2 team members
- 🐛 **BUG** hits 2 team members

### Encounter of the Day

<details>
<summary>🎲 Encounter: Snorlax</summary>

<div align="center">
<img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/143.gif" alt="Snorlax" width="150" height="150"/>
</div>

- **Rarity Signal:** Wild Encounter
- **Type Signal:** ⚪NORMAL
- **Height / Weight:** 2.1m · 460.0kg
- **Abilities:** Immunity, Thick Fat, Gluttony
- **Pokédex Insight:** Very lazy. Just eats and sleeps. As its rotund bulk builds, it becomes steadily more slothful.
- **Encounter Telemetry:** Routine scouting ping—deploy capture drones at your discretion.

</details>

### Gym Log

| Date | Challenger | Team | Result |
| --- | --- | --- | --- |
| 2025-11-24 | Gary Oak | Blastoise, Arcanine, Exeggutor | 3-0 (Arudchayan) |

### Poképaste Export

Copy this to import the current team into Pokémon Showdown:

```
Zeraora @ Expert Belt
Ability: Volt Absorb
EVs: 252 Atk / 4 Def / 252 Spe
Jolly Nature
- Thunder Wave
- Bulk Up
- Calm Mind
- Protect

Rayquaza @ Heavy-Duty Boots
Ability: Air Lock
EVs: 252 HP / 252 SpA / 4 SpD
Mild Nature
- Dragon Ascent
- Dragon Dance
- Defog
- Hurricane

Noivern @ Heavy-Duty Boots
Ability: Frisk
EVs: 252 SpA / 4 SpD / 252 Spe
Timid Nature
- Roost
- Defog
- Dragon Dance
- Hurricane

Metagross @ Leftovers
Ability: Clear Body
EVs: 252 HP / 252 Atk / 4 Def
Adamant Nature
- Bullet Punch
- Protect
- Stealth Rock
- Substitute

Gengar @ Life Orb
Ability: Cursed Body
EVs: 252 SpA / 4 SpD / 252 Spe
Timid Nature
- Toxic
- Toxic Spikes
- Shadow Ball
- Sludge Wave

Decidueye @ Leftovers
Ability: Overgrow
EVs: 252 HP / 252 Atk / 4 Def
Adamant Nature
- Synthesis
- Shadow Sneak
- Nasty Plot
- Defog
```

</details>

---

## 🗺️ How This Page Is Built

The README rebuilds itself daily at midnight UTC: `scripts/build_readme.py` picks a team from [`data/archetypes.json`](data/archetypes.json), fetches live stats from PokéAPI, renders the battle card and radar charts through [`scripts/svg_generator.py`](scripts/svg_generator.py), and commits the result via [`.github/workflows/update-readme.yml`](.github/workflows/update-readme.yml). Issues titled `Challenge @...` trigger the gym-battle workflow. The whole thing is deterministic, typed, and re-runnable — the page is part of the portfolio.

---

## 🤝 Contact

- **GitHub:** [@Arudchayan](https://github.com/Arudchayan)
- **Open to:** research engineering, ML systems, evaluation, and reinforcement learning roles.
- **Best way to reach me:** open an issue or start a discussion on any repo.

---

<sub>README last rebuilt on 2026-11-23 00:37 UTC. Next rotation triggers at midnight UTC.</sub>
