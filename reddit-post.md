# Title

I made a bot that turns your GitHub commits into a daily comic strip. Every morning I wake up to a medieval knight version of my changelog.

# Flair

Built with Claude

# Body

Every morning I've already forgotten what I shipped yesterday. So I built a bot that reads your commits and turns them into a 4-panel comic strip -- a deadpan medieval knight (you) ships code while villagers build statues in your honor for fixing a typo.

These images are from real repos. Claude Code's repo had exactly 1 commit -- "Update CHANGELOG.md." The bot turned that into 4 panels. "1 COMMIT. 1 PERIOD."

It runs on GitHub Actions (daily cron), uses Gemini for the script and image generation, and delivers via Telegram or GitHub Issues. Runs on the free Gemini tier so it costs nothing.

Setup is about 2 minutes. Fork the repo, set one secret (free Gemini API key), set one variable (the repo you want comics for), enable Actions. Tomorrow morning you get your first comic.

What surprised me: it's genuinely motivating. You wake up, open Telegram, and there's a comic about what YOU shipped yesterday. Not a generic meme -- your actual commits, turned into a story with a knight and hysterical villagers. Makes you want to ship more today so tomorrow's comic is better.

Built the whole thing with Claude Code over a weekend. Claude wrote the GitHub Actions pipeline, the Gemini integration, the Telegram delivery, and the Pillow image stitching. The only real back-and-forth was prompt engineering the comic style -- getting Gemini to produce consistent 4-panel layouts with the right tone took a few iterations. The code itself Claude nailed first try.

Why Gemini for the comics? Claude doesn't do image generation (yet). Claude Code built it, Gemini draws it.

GitHub: https://github.com/shalomer/github-comic-bot

Edit: Reddit downscales the gallery images. Full resolution panels:

- [Claude Code - 1 commit, 4 panels](https://raw.githubusercontent.com/shalomer/github-comic-bot/main/comic-strips/sample-claude-code.png)
- [Next.js - 4 commits](https://raw.githubusercontent.com/shalomer/github-comic-bot/main/comic-strips/sample-nextjs.png)
