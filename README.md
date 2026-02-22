# github-comic-bot

**Your commits deserve better than a changelog.**

Every morning, this bot reads yesterday's commits and turns them into a 4-panel medieval RPG comic strip. A calm, deadpan knight (you) fixes bugs and ships features. The villagers (your users) react with weeping, statue-building, and naming their children after git commands.

Powered entirely by **Gemini AI** — one free API key, zero config, delivered straight to your GitHub Issues.

![Sample Comic](https://github.com/shalomer/github-comic-bot/releases/download/comic-2026-02-21/2026-02-21.jpg)

> *5 real commits → 4 panels → 1 exhausted knight*

---

## Get Daily Comics in 2 Minutes

```bash
claude skill install shalomer/github-comic-bot
```

Then:

```
/daily-comic setup owner/repo
```

That's it. The setup forks this repo, configures your Gemini key, and triggers the first comic. Every morning after that, a new comic lands in your GitHub Issues — using notifications you already have.

**One-off mode** (no setup, just generate):

```
/daily-comic owner/repo
```

---

## Manual Setup (No Claude Code)

### 1. Fork this repo

```bash
gh repo fork shalomer/github-comic-bot --clone=false
```

### 2. Get a free Gemini API key

https://aistudio.google.com/app/apikey

### 3. Configure your fork

```bash
gh secret set GEMINI_API_KEY --repo YOUR_USERNAME/github-comic-bot
gh variable set TARGET_REPO --repo YOUR_USERNAME/github-comic-bot --body "owner/repo"

# Only for private repos:
gh secret set GH_PAT --repo YOUR_USERNAME/github-comic-bot
```

### 4. Enable Actions

```bash
gh api repos/YOUR_USERNAME/github-comic-bot/actions/permissions -X PUT -f enabled=true -f allowed_actions=all
```

### 5. Trigger or wait

Go to **Actions** tab → "Daily Comic Strip" → **Run workflow**

Runs automatically every day at 6:00 AM IST (00:30 UTC).

---

## How It Works

1. Fetches yesterday's commits via GitHub API
2. Gemini writes a 4-panel comic script (medieval RPG style)
3. Gemini generates each panel as an image
4. Pillow stitches panels into one strip
5. Commits the PNG to the repo
6. Creates a GitHub Issue with the comic + dialogue

## Quick Start (Local)

```bash
pip install -r requirements.txt

GEMINI_API_KEY=your-key TARGET_REPO=owner/repo python scripts/daily_comic.py
```

## Cost

**$0.** Gemini free tier + GitHub Actions free tier.

## CLI Reference

```bash
python scripts/daily_comic.py [date]              # Generate locally
python scripts/daily_comic.py --create-issue       # Post as GitHub Issue (CI)
```

---

If you enjoy this, [buy me a coffee](https://buymeacoffee.com/shalomer).
