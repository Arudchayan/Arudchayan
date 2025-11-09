# 🚀 QUICKSTART - Get Your Bonkers Pokémon Profile in 5 Minutes!

## ⚡ Super Fast Setup

### 1. Fork This Repo
Click the "Fork" button at the top right of this GitHub page.

### 2. Enable GitHub Actions
1. Go to your forked repo
2. Click **"Settings"** → **"Actions"** → **"General"**
3. Under "Workflow permissions", select **"Read and write permissions"**
4. Click **"Save"**

### 3. Enable the Workflows
1. Go to the **"Actions"** tab
2. Click **"I understand my workflows, go ahead and enable them"**

### 4. Trigger the First Build
1. Still in the **"Actions"** tab
2. Click **"Manual README Update"** in the left sidebar
3. Click **"Run workflow"** → **"Run workflow"**
4. Wait 30 seconds ⏱️

### 5. Check Your README! 🎉
Go back to your repo home page and see your BONKERS Pokémon profile!

---

## 🎯 What Happens Next?

✅ **Automatic Daily Updates** - Every midnight UTC, your team rotates!
✅ **Live Pokémon Data** - Real sprites and stats from PokéAPI
✅ **Animated GIFs** - Watch your Pokémon come to life!
✅ **Zero Maintenance** - Set it and forget it!

---

## 🎨 Customize Your Team

Edit `data/archetypes.json` to add your favorite Pokémon:

```json
{
  "id": "my-team",
  "title": "My Awesome Team",
  "lead": "Charizard",
  "team": ["Charizard", "Blastoise", "Venusaur", "Pikachu", "Snorlax", "Dragonite"],
  "tera_type": "Fire",
  "z_move": "Inferno Overdrive",
  "mega": "Charizardite X"
}
```

**Pokémon Name Format:**
- Use proper capitalization: `Pikachu`, not `pikachu`
- Don't include "Mega" prefix: `Charizard`, not `Mega Charizard`
- The script handles everything automatically!

Commit and push:
```bash
git add data/archetypes.json
git commit -m "✨ Add my custom team"
git push
```

Your README will update automatically! 🎮

---

## 🔥 Pro Tips

### Add More Teams
The more archetypes you add, the more variety in daily rotations!

### Change Update Frequency
Edit `.github/workflows/update-readme.yml`:
```yaml
schedule:
  - cron: '0 */6 * * *'  # Every 6 hours instead of daily
```

### Force an Update Anytime
1. Go to **Actions** tab
2. Click **"Manual README Update"**
3. Click **"Run workflow"**

---

## 🐛 Troubleshooting

**Workflow won't run?**
- Check Settings → Actions → General → Workflow permissions → "Read and write permissions"

**Invalid Pokémon name?**
- Check spelling against [PokéAPI](https://pokeapi.co/api/v2/pokemon/)
- Use lowercase for API testing: `https://pokeapi.co/api/v2/pokemon/charizard`

**Need help?**
- Open an issue on GitHub!
- Check `SETUP.md` for detailed troubleshooting

---

## 🎮 That's It!

You now have the most BONKERS GitHub profile with:
- 🎨 Animated Pokémon sprites
- 📊 Real battle stats
- 🔄 Daily team rotations
- 💜 Royal Purple aesthetics
- ⚡ Zero maintenance

### 💜 GOTTA CODE 'EM ALL! 💜

---

**Want more features?** Check out `SETUP.md` for advanced customization!
