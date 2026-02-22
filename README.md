# github-comic-bot

Turns your GitHub commits into a daily medieval RPG comic strip. A calm, deadpan knight fixes bugs while villagers lose their minds.

Powered entirely by **Gemini** (script writing + image generation) — only 1 API key needed.

## Install via Claude Code (Recommended)

The easiest way to get daily comics delivered to you:

```bash
claude skill install shalomer/github-comic-bot
```

Then run the setup:

```
/daily-comic setup owner/repo
```

This forks the bot, configures it for your repo, and triggers the first run. You'll get daily comics delivered as **GitHub Issues** — no email service, no Telegram, just GitHub notifications you already have.

Or generate a one-off comic locally:

```
/daily-comic owner/repo
```

## Quick Start (Local)

```bash
pip install -r requirements.txt

GEMINI_API_KEY=your-key-here \
TARGET_REPO=owner/repo \
python scripts/daily_comic.py

# Or for a specific date:
python scripts/daily_comic.py 2026-02-20
```

The comic opens automatically after generation.

## Setup (Automated Daily)

### 1. Fork this repo

```bash
gh repo fork shalomer/github-comic-bot --clone=false
```

### 2. Get a Gemini API key

Free at https://aistudio.google.com/app/apikey

### 3. Configure your fork

```bash
# Required: Gemini API key
gh secret set GEMINI_API_KEY --repo YOUR_USERNAME/github-comic-bot

# Required: which repo to make comics about
gh variable set TARGET_REPO --repo YOUR_USERNAME/github-comic-bot --body "owner/repo"

# Only for private repos: a PAT with repo read access
gh secret set GH_PAT --repo YOUR_USERNAME/github-comic-bot
```

### 4. Enable Actions on the fork

```bash
gh api repos/YOUR_USERNAME/github-comic-bot/actions/permissions -X PUT -f enabled=true -f allowed_actions=all
```

### 5. Trigger manually or wait

Go to Actions tab → "Daily Comic Strip" → "Run workflow"

Runs automatically every day at 6:00 AM IST (00:30 UTC). Each comic is posted as a **GitHub Issue** with the image embedded and panel dialogue.

## How It Works

1. Fetches yesterday's commits via GitHub API
2. Gemini writes a 4-panel comic script (medieval RPG style)
3. Gemini generates panel images
4. Pillow stitches panels horizontally
5. Saves to `comic-strips/YYYY-MM-DD.png`, commits to the repo
6. Creates a GitHub Issue with the comic image and dialogue

## Cost

- Gemini: free tier covers daily usage
- GitHub Actions: free

## Output

Comics saved to `comic-strips/YYYY-MM-DD.png` with a `.json` script file. Each comic also appears as a GitHub Issue.

## CLI Flags

```bash
python scripts/daily_comic.py [date]              # Generate comic (opens locally)
python scripts/daily_comic.py --create-issue       # Create GitHub Issue from saved JSON (used by CI)
python scripts/daily_comic.py --create-issue date  # Same, for a specific date
```

## Support

If you enjoy this, consider [buying me a coffee](https://buymeacoffee.com/shalomer).
