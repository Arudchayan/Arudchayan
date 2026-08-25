# 🎮 Pokémon Trainer Profile - Setup Guide

## 🚀 Quick Start

### 1️⃣ Fork or Clone This Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

### 2️⃣ Enable GitHub Actions

1. Go to your repository on GitHub
2. Click on **"Actions"** tab
3. Click **"I understand my workflows, go ahead and enable them"**

### 3️⃣ Push to GitHub

```bash
git push origin main
```

That's it! 🎉 The workflows will automatically:
- ✅ Generate your README daily at midnight UTC
- ✅ Update on every push to main/master
- ✅ Fetch live Pokémon data from PokéAPI
- ✅ Display animated Pokémon sprites

---

## 🔧 Configuration

### Customize Your Team

Edit `data/archetypes.json` to add your own Pokémon teams:

```json
{
  "id": "your-archetype",
  "title": "Your Cool Title",
  "lead": "YourPokemon",
  "team": [
    "Pokemon1",
    "Pokemon2",
    "Pokemon3",
    "Pokemon4",
    "Pokemon5",
    "Pokemon6"
  ],
  "tera_type": "Fire",
  "z_move": "Inferno Overdrive",
  "mega": "YourPokemonite"
}
```

### Customize the Template

Edit `README.template.md` to change:
- Text content
- ASCII art
- Layout structure
- Any static content

**Note:** Keep the placeholder tags like `{LEAD_POKEMON}` for dynamic content!

---

## 🤖 GitHub Actions Workflows

### 1. 🔄 Automatic Daily Updates (`update-readme.yml`)

**Triggers:**
- 🕐 Daily at midnight UTC (cron schedule)
- 📝 Push to main/master (only when scripts/data/template change)
- 🎯 Manual trigger via Actions tab

**What it does:**
- Runs the build script
- Fetches fresh Pokémon data from PokéAPI
- Updates README.md with new sprites and stats
- Commits and pushes changes automatically

### 2. 🎯 Manual Update (`manual-update.yml`)

**Triggers:**
- Manual dispatch only (Actions tab → Run workflow)

**Options:**
- Force regenerate even without changes

**Use when:**
- You want to test changes immediately
- You want to force a fresh generation
- You're debugging the build process

### 3. 🧪 Test Build (`test-build.yml`)

**Triggers:**
- Pull requests to main/master

**What it does:**
- Tests that the build script runs successfully
- Validates README.md output
- Shows sample output for review
- Prevents broken builds from merging

---

## 📋 Requirements

### System Requirements
- Python 3.11+ (automatically provided by GitHub Actions)
- No external Python packages needed (uses standard library only)
- Internet connection (for PokéAPI calls)

### GitHub Permissions
The workflows need `contents: write` permission to commit changes. This is automatically configured in the workflow files.

---

## 🎯 Manual Local Build

Want to test locally before pushing?

```bash
# Run the build script
python3 scripts/build_readme.py

# Check the generated README
cat README.md

# Or open in your browser
open README.md  # macOS
xdg-open README.md  # Linux
```

---

## 🐛 Troubleshooting

### Workflow Not Running?

1. **Check Actions are enabled:**
   - Go to Settings → Actions → General
   - Enable "Allow all actions and reusable workflows"

2. **Check workflow permissions:**
   - Go to Settings → Actions → General → Workflow permissions
   - Enable "Read and write permissions"

3. **Check branch name:**
   - Workflows trigger on `main` or `master` branch
   - Update `.github/workflows/*.yml` if you use a different branch name

### Build Script Fails?

1. **PokéAPI timeout:**
   - The script includes 0.5s delays between API calls
   - If it still fails, increase timeout in `scripts/build_readme.py`

2. **Invalid Pokémon name:**
   - Check `data/archetypes.json` for typos
   - Pokémon names must match PokéAPI format (lowercase, hyphens for spaces)
   - Remove "Mega" prefix - script handles it automatically

3. **Missing sprites:**
   - Script falls back to ASCII art if sprites unavailable
   - Check the Pokémon exists in PokéAPI

### README Not Updating?

1. **Check recent workflow runs:**
   - Go to Actions tab
   - Click on latest workflow run
   - Check logs for errors

2. **Force a manual update:**
   - Go to Actions tab
   - Click "Manual README Update"
   - Click "Run workflow"
   - Enable "Force regenerate"

---

## 🎨 Customization Ideas

### Add More Archetypes
Add more team configurations to rotate through more frequently!

### Change the Schedule
Edit the cron schedule in `update-readme.yml`:
```yaml
schedule:
  - cron: '0 */6 * * *'  # Every 6 hours
  - cron: '0 12 * * *'   # Daily at noon UTC
  - cron: '0 0 * * 1'    # Weekly on Monday
```

### Add Shiny Sprites
Modify `scripts/build_readme.py` to use shiny sprites:
```python
sprite_url = sprites.get('front_shiny')  # Use shiny instead
```

### Add More Pokémon Data
Fetch additional data from PokéAPI:
- Evolution chains
- Egg groups
- Habitat information
- Pokédex numbers from different regions

---

## 🌟 Features

✅ **100% Open Source** - No API keys needed
✅ **Animated Sprites** - GIF animations from PokéAPI
✅ **Daily Rotation** - Different archetype each day
✅ **Deterministic** - Same team on the same date
✅ **Automatic** - Zero maintenance required
✅ **Customizable** - Easy to modify
✅ **Fast** - Generates in seconds
✅ **Reliable** - Fallbacks for everything

---

## 📚 Resources

- [PokéAPI Documentation](https://pokeapi.co/docs/v2)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Markdown Guide](https://www.markdownguide.org/)
- [Shields.io Badges](https://shields.io/)

---

## 💜 Credits

- **PokéAPI** - Amazing free Pokémon data API
- **Pokémon Sprites** - From PokéAPI GitHub repository
- **Royal Purple Theme** - #6A0DAD hex color
- **Made with** - Python, Caffeine, and Love for Pokémon

---

<div align="center">

## 🎮 GOTTA CODE 'EM ALL! 🎮

**Made with 💜 and way too much coffee**

</div>
