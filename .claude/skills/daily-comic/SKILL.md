---
name: daily-comic
description: Generate a comic strip from yesterday's GitHub commits. Turns commits into a medieval RPG 4-panel comic using Gemini.
user-invocable: true
allowed-tools: Bash, Read, Write
argument-hint: [owner/repo] [date]
---

# Daily Comic Strip Generator

Generate a 4-panel medieval RPG comic strip from a GitHub repo's commits.

## Usage

```
/daily-comic owner/repo
/daily-comic owner/repo 2026-02-20
```

- First argument: GitHub repo (e.g. `octocat/hello-world`)
- Second argument (optional): date in YYYY-MM-DD format (defaults to yesterday)

## Requirements

The user needs `GEMINI_API_KEY` set in their environment. If not set, tell them to get a free key at https://aistudio.google.com/app/apikey and set it:

```bash
export GEMINI_API_KEY=your-key-here
```

For private repos, `GITHUB_TOKEN` must also be set (or `gh auth` must be logged in).

## Steps

1. **Check prerequisites**: Verify `GEMINI_API_KEY` is set. If not, stop and tell the user how to get one.

2. **Install dependencies** (if needed):
```bash
pip install google-genai Pillow requests 2>/dev/null
```

3. **Fetch commits**: Run this to get yesterday's commits from the target repo:
```bash
REPO="$ARGUMENTS[0]"
DATE="${ARGUMENTS[1]:-$(date -u -v-1d +%Y-%m-%d 2>/dev/null || date -u -d 'yesterday' +%Y-%m-%d)}"
```
Use the GitHub API via `curl` or the `gh` CLI to fetch commits for that date. Filter out merge commits.

If 0 commits found, tell the user "No commits found for {date}. No comic today." and stop.

4. **Generate comic script**: Call Gemini (`gemini-2.0-flash`) with the commit list to generate a 4-panel comic script as JSON. Use this system prompt:

> You are a comedy writer for a daily comic strip about GitHub commits.
> SETTING: A medieval fantasy kingdom where a calm, deadpan knight (the developer) fixes bugs and builds features. The villagers (users) react with absurd, over-the-top emotions to every change.
> Create a 4-panel comic. Panels 1-3: pick the 3 funniest commits. Panel 4: summary with exhausted knight and statue-building villagers.
> Each panel: title (commit message), scene (vivid image gen description), bubbles (2-3 speech bubbles).
> Knight = always calm, deadpan. Villagers = always losing their minds.
> Return ONLY a JSON array of 4 panel objects.

5. **Generate 4 images**: For each panel, call Gemini image generation (`gemini-2.0-flash-exp-image-generation`) with:
```
"Cartoon style, warm tones (coral, gold, cream), bold outlines, simple and clear, medieval fantasy village setting. TOP TITLE BAR (black bar with white text): '{title}'. {scene} Speech bubbles: {bubbles}"
```

6. **Stitch panels**: Use Pillow to stitch all panel images horizontally with a 20px white gap. Save as `comic-strips/YYYY-MM-DD.png` in the current directory.

7. **Open the result**: Open the PNG with the system viewer (`open` on macOS, `xdg-open` on Linux).

8. **Show the user**: Tell them where the comic was saved and show the panel titles/dialogue.

## Important

- Use `scripts/daily_comic.py` if it exists in the current repo (saves reimplementing everything).
- If running from a different repo, create a temp Python script with the full pipeline logic.
- Always save output to `comic-strips/` directory.
- If Gemini image generation fails for a panel, retry up to 3 times with 5s delays.
- Need at least 2 panels to produce a comic.
