<p align="center"><img src="assets/hero.svg?v=739943" width="880" alt="Arudchayan — ML research engineer. 2,003/2,003 speech playback; 0.60 → 0.00 blinded detection; 16/16 agent boundary. Open to research engineering roles."/></p>

<p align="center"><sub><strong>2,003/2,003</strong> speech playback · <strong>0.60 → 0.00</strong> blinded detection · <strong>16/16</strong> agent boundary</sub></p>

<p align="center"><sub>Evaluation harnesses for small models · monitorability &amp; agent safety · open to research engineering roles</sub></p>

## 01 · Selected research

### [Turnwave](https://github.com/Arudchayan/Turnwave)
<sub><code>Python</code> · <code>evals</code> · public</sub>

Local speech-to-speech research on LFM2.5-Audio-1.5B: streaming audio, interruption handling, Silero VAD, and a replayable eval harness.

> **Finding:** final-block playback race **0/2,003 → 2,003/2,003** samples played, regression-tested.

### TraceScope
<sub><code>Python</code> · <code>evals</code> · private R&amp;D · write-up on request</sub>

Small-LM safety-monitor evals: judge seed variance, prompt brittleness, and embedding-monitor transfer limits.

> **Finding:** reassuring summaries blind every monitor tested — detection **0.60 → 0.00** across keyword, embedding, and 0.5B-judge monitors.

### AgentGate
<sub><code>Python</code> · <code>agent security</code> · private R&amp;D · write-up on request</sub>

Enforcement gate for agent file/email actions: allowlists, sensitive-pattern confirms, and measured block/legit rates.

> **Finding:** 2/2 exfiltration tasks blocked + 14/14 boundary cases = **16/16**; every bypass logged beside its fix.

### WarningTime
<sub><code>Python</code> · <code>evals</code> · private R&amp;D · write-up on request</sub>

Trajectory-monitor metrics that separate detection from prevention.

> **Finding:** strict monitors raised false alarms on **3 of 47** benign trajectories; lenient monitors arrive up to **3 steps** late.

## 02 · Apparatus & tooling

**[adam-mcp](https://github.com/Arudchayan/adam-mcp)** · <sub><code>TypeScript</code> · <code>MCP</code> · <a href="https://www.npmjs.com/package/adam-mcp">npm</a></sub>
Local-first, read-only MCP server for University of Basel ADAM. SWITCH edu-ID stays in the browser. **npm 0.5.0** · 71 commits and 71 PRs in the last 30 days.

**[ResearchQuest](https://github.com/Arudchayan/ResearchQuest)** · <sub><code>React 19</code> · <code>Supabase</code> · <a href="https://rq.arudchayan.com">live demo</a></sub>
Scholarly workspace for papers, notes, ideas, a Today plan, Focus Studio, and DOI/Crossref import. **Live demo** · realtime Supabase workspace.

<sub>**Also shipped:** <a href="https://github.com/Arudchayan/overstay">overstay</a> v0.2.1 · <a href="https://baselcal.vercel.app">BASELCAL</a> · <a href="https://github.com/Arudchayan/ResumeBuilder">ResumeBuilder</a></sub>

## 03 · Field notes

<p align="center"><img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/807.gif" alt="Zeraora" width="72" height="72"/> <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/384.gif" alt="Rayquaza" width="72" height="72"/> <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/715.gif" alt="Noivern" width="72" height="72"/> <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/376.gif" alt="Metagross" width="72" height="72"/> <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/94.gif" alt="Gengar" width="72" height="72"/> <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/showdown/724.gif" alt="Decidueye" width="72" height="72"/></p>

**Seed 739943** · Thunderborn Storm Raider · **Zeraora** lead · 🔥 Harsh Sunlight
**Roster:** Zeraora, Rayquaza, Noivern, Metagross, Gengar, Decidueye
**Quest:** Push a commit before noon to outspeed Rival Weavile.

<details>
<summary>Open the full trainer card — squad dossiers, type intel, gym log</summary>

### Squad dossiers

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
  - 🥊 Close Combat · Physical · 120 BP
  - 🌙 Knock Off · Physical · 65 BP
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
- **Ability:** Infiltrator
- **Nature:** Timid
- **Held Item:** Heavy-Duty Boots
- **EV Spread:** 252 SpA / 4 SpD / 252 Spe
- **Signature Moves:**
  - 🕊️ Roost · Status · Utility
  - 🕊️ Defog · Status · Utility
  - 🕊️ Hurricane · Special · 110 BP
  - 🐉 Dragon Pulse · Special · 85 BP
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
  - 🌍 Earthquake · Physical · 100 BP
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
- **Ability:** Long Reach
- **Nature:** Adamant
- **Held Item:** Leftovers
- **EV Spread:** 252 HP / 252 Atk / 4 Def
- **Signature Moves:**
  - 🌿 Synthesis · Status · Utility
  - 👻 Shadow Sneak · Physical · 40 BP
  - 🌙 Nasty Plot · Status · Utility
  - 🕊️ Brave Bird · Physical · 120 BP
</details>

### Type coverage &amp; defensive analysis

- 🐉 **DRAGON** ×2
- 🕊️ **FLYING** ×2
- 👻 **GHOST** ×2
- ⚡ **ELECTRIC** ×1
- ⚙️ **STEEL** ×1
- 🔮 **PSYCHIC** ×1
- ☠️ **POISON** ×1
- 🌿 **GRASS** ×1

### ⚠️ Critical Weaknesses (3+ Pokemon)
- 🌍 **GROUND** threatens 3 team members
- 🧊 **ICE** threatens 3 team members
- 🌙 **DARK** threatens 3 team members
- 👻 **GHOST** threatens 3 team members

### ⚡ Moderate Weaknesses (2 Pokemon)
- 🐉 **DRAGON** hits 2 team members
- 🪨 **ROCK** hits 2 team members
- ⚡ **ELECTRIC** hits 2 team members
- ✨ **FAIRY** hits 2 team members
- 🐛 **BUG** hits 2 team members
- 🔥 **FIRE** hits 2 team members

### Encounter of the day

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

### Gym log

| Date | Challenger | Team | Result |
| --- | --- | --- | --- |
| 2025-11-24 | Gary Oak | Blastoise, Arcanine, Exeggutor | 3-0 (Arudchayan) |

### Poképaste export

Copy this to import the current team into Pokémon Showdown:

```
Zeraora @ Expert Belt
Ability: Volt Absorb
EVs: 252 Atk / 4 Def / 252 Spe
Jolly Nature
- Thunder Wave
- Bulk Up
- Close Combat
- Knock Off

Rayquaza @ Heavy-Duty Boots
Ability: Air Lock
EVs: 252 HP / 252 SpA / 4 SpD
Mild Nature
- Dragon Ascent
- Dragon Dance
- Defog
- Hurricane

Noivern @ Heavy-Duty Boots
Ability: Infiltrator
EVs: 252 SpA / 4 SpD / 252 Spe
Timid Nature
- Roost
- Defog
- Hurricane
- Dragon Pulse

Metagross @ Leftovers
Ability: Clear Body
EVs: 252 HP / 252 Atk / 4 Def
Adamant Nature
- Bullet Punch
- Protect
- Stealth Rock
- Earthquake

Gengar @ Life Orb
Ability: Cursed Body
EVs: 252 SpA / 4 SpD / 252 Spe
Timid Nature
- Toxic
- Toxic Spikes
- Shadow Ball
- Sludge Wave

Decidueye @ Leftovers
Ability: Long Reach
EVs: 252 HP / 252 Atk / 4 Def
Adamant Nature
- Synthesis
- Shadow Sneak
- Nasty Plot
- Brave Bird
```

</details>

## 04 · Colophon

The README rebuilds itself daily in GitHub Actions: [`scripts/build_readme.py`](scripts/build_readme.py) picks a team from [`data/archetypes.json`](data/archetypes.json), fetches live stats from PokéAPI, renders the field-guide plate and radar cards through [`scripts/svg_generator.py`](scripts/svg_generator.py), and commits the result via [`.github/workflows/update-readme.yml`](.github/workflows/update-readme.yml). Issues titled `Challenge @...` trigger the gym-battle workflow. It is seeded from the date, re-runnable, and fully automated — the page is itself part of the portfolio.

## Contact

- **GitHub:** [@Arudchayan](https://github.com/Arudchayan)
- **LinkedIn:** [in/arudchayan](https://www.linkedin.com/in/arudchayan/)
- **Open to:** research engineering, ML systems, evaluation, and reinforcement learning roles.
- **Best way to reach me:** a LinkedIn message or an issue/discussion on any repo.

---

<sub>README last rebuilt on 2026-11-23 07:14 UTC. The next daily rotation is generated by GitHub Actions.</sub>
