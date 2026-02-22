# github-comic-bot

Turns your GitHub commits into a daily medieval RPG comic strip. A calm, deadpan knight fixes bugs while villagers lose their minds.

Powered entirely by **Gemini** (script writing + image generation) — only 1 API key needed.

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

### 1. Get a Gemini API key
Free at https://aistudio.google.com/app/apikey

### 2. Add GitHub secrets
```bash
gh secret set GEMINI_API_KEY       # from step 1
gh secret set GH_PAT               # GitHub PAT with repo read scope (only needed for private repos)
```

### 3. Manual trigger
Go to Actions tab → "Daily Comic Strip" → "Run workflow"

Runs automatically every day at 6:00 AM IST (00:30 UTC).

## Claude Code Skill

Install as a Claude Code skill to generate comics from any repo:

```bash
claude skill install shalomer/github-comic-bot
```

Then in Claude Code:
```
/daily-comic owner/repo
```

## How It Works

1. Fetches yesterday's commits via GitHub API
2. Gemini writes a 4-panel comic script (medieval RPG style)
3. Gemini generates panel images
4. Pillow stitches panels horizontally
5. Saves to `comic-strips/YYYY-MM-DD.png` and opens it

## Cost
- Gemini: free tier covers daily usage
- GitHub Actions: free

## Output
Comics saved to `comic-strips/YYYY-MM-DD.png` with a `.json` script file.

## Support
If you enjoy this, consider [buying me a coffee](https://buymeacoffee.com/shalomer).
