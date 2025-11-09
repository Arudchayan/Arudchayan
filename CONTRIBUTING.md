# Contributing

Issues and PRs are welcome! Theme is **Royal Purple**—keep assets and badges aligned to hex `#6A0DAD`.

## 🎮 How to Contribute

### Reporting Issues
- 🐛 Found a bug? Open an issue!
- 💡 Have an idea? Share it!
- ❓ Need help? Ask away!

### Contributing Code

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Test locally:** `python3 scripts/build_readme.py`
5. **Commit with emoji:** `git commit -m "✨ Add amazing feature"`
6. **Push to branch:** `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Adding New Archetypes

Edit `data/archetypes.json`:

```json
{
  "id": "unique-id",
  "title": "Your Awesome Title",
  "lead": "YourPokemon",
  "team": ["Pokemon1", "Pokemon2", "Pokemon3", "Pokemon4", "Pokemon5", "Pokemon6"],
  "tera_type": "Fire",
  "z_move": "Optional Z-Move Name",
  "mega": "Optional Mega Stone"
}
```

### Modifying the Template

Edit `README.template.md` and use these placeholders:
- `{LEAD_POKEMON}` - Lead Pokémon name
- `{TEAM_LIST}` - Comma-separated team
- `{LEAD_ASCII}` - Pokémon sprite/image
- See `scripts/build_readme.py` for full list

### Testing Workflows

The `test-build.yml` workflow runs automatically on PRs to validate changes.

## 🎨 Style Guidelines

- 💜 Use Royal Purple (#6A0DAD) for branding
- 🎯 Keep the Pokémon theme consistent
- ✨ Add ASCII art and emojis liberally
- 🎮 Make it BONKERS and FUN!

## 📝 Commit Message Format

Use emoji prefixes:
- ✨ New feature
- 🐛 Bug fix
- 📝 Documentation
- 🎨 Style/formatting
- ⚡ Performance
- 🔧 Configuration
- 🎮 Pokémon-related changes

## 🤝 Code of Conduct

Be excellent to each other! 🎉

## 💜 Thank You!

Your contributions make this project more awesome! 🚀
