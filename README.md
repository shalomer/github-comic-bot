# github-comic-bot

**Your commits deserve better than a changelog.**

Every morning, this bot reads yesterday's commits and turns them into a 4-panel medieval RPG comic strip -- delivered to your Telegram or GitHub Issues. Powered entirely by Gemini AI. Costs $0.

![Sample Comic](https://raw.githubusercontent.com/shalomer/github-comic-bot/main/comic-strips/2026-03-31.png)

> *198 commits from [openclaw/openclaw](https://github.com/openclaw/openclaw). 4 panels. 1 exhausted knight.*

A calm, deadpan knight (you) fixes bugs and ships features. The villagers (your users) react with weeping, statue-building, and naming their children after git commands.

---

## Setup (2 minutes)

You need two things:

1. **Gemini API key** (free) -- [get one here](https://aistudio.google.com/app/apikey)
2. **Telegram bot** (optional) -- message [@BotFather](https://t.me/botfather) to create one

**Step 1: Fork and configure**

```bash
# Fork the repo
gh repo fork shalomer/github-comic-bot --clone=false

# Set your Gemini key
gh secret set GEMINI_API_KEY --repo YOUR_USERNAME/github-comic-bot

# Set the repo you want comics for (e.g. "octocat/hello-world")
# This is the repo whose commits get turned into comics -- NOT the fork itself
gh variable set TARGET_REPO --repo YOUR_USERNAME/github-comic-bot --body "owner/repo"
```

**Step 2: Enable Actions and trigger**

```bash
gh api repos/YOUR_USERNAME/github-comic-bot/actions/permissions -X PUT -f enabled=true -f allowed_actions=all
```

Go to **Actions** tab > "Daily Comic Strip" > **Run workflow**.

Runs automatically every day at 00:30 UTC. That's it.

### Telegram delivery

Add these secrets to your fork and comics will land in your Telegram chat every morning:

```bash
gh secret set TELEGRAM_BOT_TOKEN --repo YOUR_USERNAME/github-comic-bot
gh secret set TELEGRAM_CHAT_ID --repo YOUR_USERNAME/github-comic-bot
```

To find your chat ID: send any message to your bot, then open `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` in your browser.

---

## How it works

1. GitHub Actions runs daily, fetches yesterday's commits
2. Gemini writes a 4-panel comic script (medieval RPG style)
3. Gemini generates each panel as an image
4. Pillow stitches the panels into one strip
5. Delivered via Telegram and/or GitHub Issue

## Run locally

```bash
pip install -r requirements.txt
GEMINI_API_KEY=your-key TARGET_REPO=owner/repo python scripts/daily_comic.py
```

## Private repos

If your target repo is private, add a GitHub PAT:

```bash
gh secret set GH_PAT --repo YOUR_USERNAME/github-comic-bot
```

## Cost

**$0.** Gemini free tier + GitHub Actions free tier.

## License

MIT

---

Built with [Claude Code](https://claude.ai/code).
