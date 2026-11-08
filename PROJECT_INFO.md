# 🎮 Pokémon Trainer Profile - Project Overview

## 📁 Project Structure

```
.
├── 📄 README.md                    # Generated profile (updated daily)
├── 📄 README.template.md           # Template for generation
├── 📄 QUICKSTART.md               # 5-minute setup guide
├── 📄 SETUP.md                    # Detailed setup & customization
├── 📄 PROJECT_INFO.md             # This file - project overview
├── 📄 CONTRIBUTING.md             # How to contribute
├── 📄 requirements.txt            # Python dependencies (none needed!)
├── 📄 LICENSE                     # MIT License
│
├── 📂 .github/
│   ├── 📂 workflows/              # GitHub Actions automation
│   │   ├── update-readme.yml     # ⚡ Main daily update
│   │   ├── test-build.yml        # 🧪 PR testing
│   └── WORKFLOWS.md              # Workflow documentation
│
├── 📂 scripts/
│   └── build_readme.py           # 🐍 README generator script
│
└── 📂 data/
    └── archetypes.json           # 🎯 Pokémon team configurations
```

---

## 🎯 Key Files Explained

### 🔴 DO NOT EDIT
- **`README.md`** - Auto-generated daily, changes will be overwritten!

### 🟢 SAFE TO EDIT
- **`data/archetypes.json`** - Add your custom Pokémon teams here
- **`README.template.md`** - Modify the layout and design
- **`scripts/build_readme.py`** - Customize generation logic

### 📘 DOCUMENTATION
- **`QUICKSTART.md`** - Start here! 5-minute setup
- **`SETUP.md`** - Detailed configuration guide
- **`CONTRIBUTING.md`** - How to contribute
- **`.github/WORKFLOWS.md`** - Workflow reference

---

## ⚡ How It Works

### 1. Daily Rotation System
```
Day Number → Deterministic Selection → Archetype Index
   └─> Same date always shows same team
```

**Example:**
- Day 739564 → Index 4 → "Ultrasonic Night Raider" (Noivern)
- Day 739565 → Index 5 → "Thunderborn Storm Raider" (Zeraora)
- Day 739566 → Index 0 → "Quantum Steel Prophet" (Metagross)

### 2. PokéAPI Integration
```
Build Script → PokéAPI → Fetch Data → Generate HTML → Update README
      ↓
  - Animated sprites (GIF)
  - Base stats with bars
  - Types & abilities
  - Moves & flavor text
  - Random encounter
```

### 3. GitHub Actions Automation
```
Midnight UTC → Trigger Workflow → Run Build Script → Commit Changes
                     ↓
              📧 Get notified if fails
```

---

## 🎨 Customization Guide

### Add a New Pokémon Team

Edit `data/archetypes.json`:

```json
{
  "id": "my-cool-team",
  "title": "Rainbow Warriors",
  "lead": "Ho-Oh",
  "team": ["Ho-Oh", "Lugia", "Celebi", "Suicune", "Entei", "Raikou"],
  "tera_type": "Fire",
  "z_move": "Inferno Overdrive",
  "mega": null
}
```

**Tips:**
- Use exact Pokémon names from [PokéAPI](https://pokeapi.co/docs/v2#pokemon)
- Don't include "Mega" prefix in names
- `z_move` and `mega` can be `null`
- More teams = more daily variety!

### Modify the Template

`README.template.md` uses placeholders:

| Placeholder | Description | Example Output |
|------------|-------------|----------------|
| `{LEAD_POKEMON}` | Lead Pokémon name | `Charizard` |
| `{LEAD_ASCII}` | Pokémon sprite image | `<img src="...">` |
| `{LEAD_TYPES}` | Type badges | `🔥FIRE 🕊️FLYING` |
| `{TEAM_LIST}` | Full team | `Charizard, Blastoise, ...` |
| `{TERA_TYPE}` | Terastallization type | `Fire` |
| `{MEGA_INFO}` | Mega evolution item | `Charizardite X` |
| `{ZMOVE_INFO}` | Z-Move name | `Inferno Overdrive` |

See `scripts/build_readme.py` for the complete list!

### Change Update Schedule

Edit `.github/workflows/update-readme.yml`:

```yaml
schedule:
  - cron: '0 */6 * * *'   # Every 6 hours
  - cron: '0 0,12 * * *'  # Twice daily (midnight & noon)
  - cron: '0 0 * * 1'     # Weekly on Monday
```

[Crontab Guru](https://crontab.guru/) - Schedule helper

---

## 🔥 Features

### Current Features ✅
- ✅ Daily archetype rotation (6 archetypes included)
- ✅ Animated Pokémon sprites from PokéAPI
- ✅ Real base stats with visual bars
- ✅ Type badges with emojis
- ✅ Move lists and abilities
- ✅ Mega Evolution tracking
- ✅ Z-Move protocols
- ✅ Terastallization display
- ✅ Random daily encounter
- ✅ Royal Purple (#6A0DAD) theme
- ✅ Fully automated via GitHub Actions
- ✅ Zero external dependencies
- ✅ 100% open source

### Possible Enhancements 💡
- 🎯 Shiny sprite variants
- 🎯 Evolution chains
- 🎯 Type matchup calculator
- 🎯 Regional form support
- 🎯 Dynamax/Gigantamax display
- 🎯 Pokédex completion tracker
- 🎯 Battle tower challenge mode
- 🎯 Seasonal event themes

---

## 🐛 Common Issues

### Issue: Workflow doesn't run
**Solution:**
1. Settings → Actions → General
2. Enable "Read and write permissions"
3. Save and trigger manual workflow

### Issue: Invalid Pokémon name
**Solution:**
- Test at: `https://pokeapi.co/api/v2/pokemon/POKEMON_NAME`
- Use lowercase, replace spaces with hyphens
- Check spelling!

### Issue: Sprites not loading
**Solution:**
- Sprites are hosted on GitHub (PokeAPI/sprites)
- May take a moment to load first time
- Check browser console for errors

### Issue: README not updating
**Solution:**
1. Check Actions tab for failed runs
2. View logs for error details
3. Test locally: `python3 scripts/build_readme.py`
4. Open an issue with error log

---

## 🔗 External Resources

### APIs Used
- **[PokéAPI](https://pokeapi.co/)** - Pokémon data (no key needed!)
- **[PokéAPI Sprites](https://github.com/PokeAPI/sprites)** - Hosted on GitHub

### Badges & Graphics
- **[Shields.io](https://shields.io/)** - Badge generation
- **[GitHub Profile README Generator](https://rahuldkjain.github.io/gh-profile-readme-generator/)** - Inspiration

### Tools
- **[Crontab Guru](https://crontab.guru/)** - Cron schedule helper
- **[JSON Validator](https://jsonlint.com/)** - Validate archetypes.json
- **[Markdown Live Preview](https://markdownlivepreview.com/)** - Test README locally

---

## 📊 Statistics

- **Total Lines:** ~800 lines generated
- **File Size:** ~26KB
- **API Calls:** 7 per build (6 team + 1 random)
- **Build Time:** ~5-10 seconds
- **Sprites:** Animated GIFs (Gen 5 Black/White or Showdown)
- **Update Frequency:** Daily at midnight UTC

---

## 💜 Credits & Inspiration

**Built With:**
- Python 3.11+
- GitHub Actions
- PokéAPI (open source Pokémon data)
- Royal Purple theme (#6A0DAD)
- Love for Pokémon & coding

**Inspired By:**
- Classic Pokémon games
- GitHub profile README trend
- Over-the-top gaming UIs
- Developer community awesomeness

---

## 📝 License

MIT License - Feel free to use, modify, and share!

---

## 🎮 Version History

- **v2.0** (2025-11-09) - Added PokéAPI integration, animated sprites, CI/CD
- **v1.0** (Earlier) - Initial ASCII art version with basic rotation

---

<div align="center">

## 🌟 MADE WITH 💜 AND POKÉMON 🌟

### ⚡ GOTTA CODE 'EM ALL! ⚡

**Questions? Open an issue!**  
**Want to contribute? Check CONTRIBUTING.md!**  
**Need help? Read SETUP.md!**

</div>