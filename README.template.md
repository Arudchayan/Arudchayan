{HERO_BANNER}

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

<p align="center">{TEAM_SPRITES}</p>

**Day {DAY_NUMBER}** · {ARCHETYPE_TITLE} · **{LEAD_POKEMON}** lead · {WEATHER_EMOJI} {WEATHER_NAME}
**Roster:** {TEAM_LIST}
**Quest:** {QUEST_TEXT}

<details>
<summary>⚔️ Open the full trainer card — squad dossiers, type intel, gym log</summary>

### Squad Dossiers

{TEAM_DETAIL_BLOCK}

### Type Coverage & Defensive Analysis

{TYPE_COVERAGE_BLOCK}

{WEAKNESS_ANALYSIS}

### Encounter of the Day

<details>
<summary>{ENCOUNTER_SUMMARY}</summary>

<div align="center">
{RANDOM_POKEMON_ASCII}
</div>

- **Rarity Signal:** {ENCOUNTER_RARITY}
- **Type Signal:** {RANDOM_POKEMON_TYPES}
- **Height / Weight:** {RANDOM_POKEMON_HEIGHT} · {RANDOM_POKEMON_WEIGHT}
- **Abilities:** {RANDOM_POKEMON_ABILITIES}
- **Pokédex Insight:** {RANDOM_POKEMON_FLAVOR}
- **Encounter Telemetry:** {ENCOUNTER_SIGNAL}

</details>

### Gym Log

{CHALLENGER_LIST}

### Poképaste Export

Copy this to import the current team into Pokémon Showdown:

{POKEPASTE_LINK}

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

<sub>README last rebuilt on {CURRENT_DATE}. Next rotation triggers at midnight UTC.</sub>
