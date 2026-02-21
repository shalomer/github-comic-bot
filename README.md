# github-comic-bot

Automated daily comic strip generator that turns GitHub commits into a medieval RPG comic strip.

Every morning, a GitHub Actions cron job:
1. Reads yesterday's commits from the vibeCoach repo
2. Uses Claude to write a funny 4-panel comic script
3. Generates images with Gemini
4. Stitches them into a horizontal strip
5. Sends the strip to Telegram

## Setup

### 1. Create Telegram bot
- Message @BotFather on Telegram → `/newbot`
- Save the bot token

### 2. Get Telegram chat ID
```bash
# Send any message to your bot first, then:
curl https://api.telegram.org/bot<TOKEN>/getUpdates
# Extract chat.id from the response
```

### 3. Add GitHub secrets
```bash
gh secret set ANTHROPIC_API_KEY    # console.anthropic.com
gh secret set GEMINI_API_KEY       # aistudio.google.com/app/apikey
gh secret set TELEGRAM_BOT_TOKEN   # from @BotFather
gh secret set TELEGRAM_CHAT_ID     # from getUpdates
gh secret set GH_PAT               # GitHub PAT with repo scope (needed to read private vibeCoach repo)
```

> **Note:** The default `GITHUB_TOKEN` in Actions is scoped to the comic-bot repo only.
> Since the vibeCoach repo is private, you need a Personal Access Token (PAT) with `repo` scope.
> Create one at https://github.com/settings/tokens → Fine-grained → select `shalomer/social-confidence-coach-v2` → Contents: Read-only.

### 4. Test locally
```bash
pip install -r requirements.txt

ANTHROPIC_API_KEY=... \
GEMINI_API_KEY=... \
TELEGRAM_BOT_TOKEN=... \
TELEGRAM_CHAT_ID=... \
TARGET_REPO=shalomer/social-confidence-coach-v2 \
python scripts/daily_comic.py

# Or test with a specific date:
python scripts/daily_comic.py 2026-02-20
```

### 5. Manual trigger
Go to Actions tab → "Daily Comic Strip" → "Run workflow"

## Cost
- Claude Sonnet: ~$0.01-0.03/day
- Gemini image gen: free tier
- Telegram: free
- GitHub Actions: free (well under 2000 min/month)
- **Total: ~$1/month**

## Output
Comics are saved to `comic-strips/YYYY-MM-DD.png` with a corresponding `.json` script file.
