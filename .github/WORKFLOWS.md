# 🤖 GitHub Actions Workflows

## 🔥 Active Workflows (Pokémon Profile)

### ⚡ `update-readme.yml` - Main Daily Update
**Status:** ✅ Active  
**Schedule:** Daily at midnight UTC + on push  
**Purpose:** Generates your Pokémon trainer profile with live PokéAPI data

**Triggers:**
- 🕐 Automatic: Daily at 00:00 UTC
- 📝 Automatic: Push to main/master (when scripts/data/template change)
- 🎯 Manual: Via Actions tab

### 🎯 `manual-update.yml` - Manual Trigger
**Status:** ✅ Active  
**Purpose:** Force regenerate your profile anytime

**Triggers:**
- 🎮 Manual only: Actions tab → "Manual README Update" → Run workflow

**Options:**
- Force regenerate even without changes

### 🧪 `test-build.yml` - PR Testing
**Status:** ✅ Active  
**Purpose:** Validates README generation on pull requests

**Triggers:**
- 🔍 Automatic: On pull requests to main/master

---

## 🎨 Optional Workflows (Legacy Features)

These workflows are from the original template and are **optional**. They won't interfere with your Pokémon profile.

### 🐍 `snake.yml` - Contribution Snake
**Status:** ⚠️ Optional (requires username update)  
**Schedule:** Daily at 01:00 UTC  
**Purpose:** Generates animated contribution snake graphic

**To enable:**
1. Create `assets/` directory
2. Update `github_user_name` in the workflow to your username
3. Uncomment the snake section in README template if you want to display it

### 📝 `blog.yml` - Blog Post Feed
**Status:** ⚠️ Optional (requires RSS feed)  
**Schedule:** Daily at 03:00 UTC  
**Purpose:** Updates README with latest blog posts from RSS feed

**To enable:**
1. Go to Settings → Secrets → Actions
2. Add secret `BLOG_RSS` with your blog's RSS feed URL
3. The workflow will automatically activate

### 📊 `metrics.yml` - GitHub Metrics
**Status:** ⚠️ Optional (requires metrics token)  
**Purpose:** Generates detailed GitHub metrics SVG

**To enable:**
1. Get a token from [metrics documentation](https://github.com/lowlighter/metrics)
2. Add `METRICS_TOKEN` secret
3. Create `assets/` directory

### ⏱️ `wakatime.yml` - WakaTime Stats
**Status:** ⚠️ Optional (requires WakaTime)  
**Purpose:** Shows coding time statistics

**To enable:**
1. Sign up for [WakaTime](https://wakatime.com)
2. Add `WAKATIME_API_KEY` secret
3. Install WakaTime plugin in your editor

---

## 🔧 Workflow Management

### Disable Optional Workflows

If you don't want the optional workflows, you can:

**Option 1: Delete them**
```bash
rm .github/workflows/blog.yml
rm .github/workflows/snake.yml
rm .github/workflows/metrics.yml
rm .github/workflows/wakatime.yml
```

**Option 2: Disable in GitHub**
1. Go to Actions tab
2. Click on workflow name
3. Click "..." menu → "Disable workflow"

### Required Permissions

All workflows need `contents: write` permission:
1. Settings → Actions → General
2. Workflow permissions → "Read and write permissions"
3. Save

---

## 📊 Workflow Status

Check workflow status:
- Go to **Actions** tab
- Green ✅ = Success
- Red ❌ = Failed (click for details)
- Yellow ⚠️ = In progress

View logs:
- Click on workflow run
- Click on job name
- Expand steps to see details

---

## 🐛 Troubleshooting

### Workflow Won't Run?
1. Check Actions are enabled (Settings → Actions)
2. Check workflow permissions (Settings → Actions → General)
3. Verify branch name in workflow triggers

### Build Fails?
1. Check Actions tab for error logs
2. Verify `data/archetypes.json` is valid JSON
3. Test locally: `python3 scripts/build_readme.py`

### Conflicts Between Workflows?
The Pokémon profile workflow (`update-readme.yml`) and optional workflows shouldn't conflict as they:
- Run at different times
- Modify different parts of README (via marked sections)
- Have built-in `[skip ci]` tags to prevent loops

---

## 💜 Workflow Priority

If you're starting fresh, we recommend:

**Essential:**
- ✅ `update-readme.yml` - Your main Pokémon profile
- ✅ `manual-update.yml` - Manual control
- ✅ `test-build.yml` - Quality assurance

**Optional (enable if you want):**
- ⭐ `snake.yml` - Cool contribution visualization
- ⭐ `blog.yml` - If you have a blog
- ⭐ `metrics.yml` - Advanced GitHub stats
- ⭐ `wakatime.yml` - Coding time tracking

---

<div align="center">

## 🎮 GOTTA CODE 'EM ALL! 🎮

**Your Pokémon profile is powered by GitHub Actions magic! ✨**

</div>
