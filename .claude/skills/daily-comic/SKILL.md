---
name: daily-comic
description: Generate a comic strip from GitHub commits, or set up automated daily delivery via GitHub Issues.
user-invocable: true
allowed-tools: Bash, Read, Write, AskUserQuestion
argument-hint: [setup] owner/repo [date]
---

# Daily Comic Strip Generator

Two modes: one-off local generation, or automated daily delivery via GitHub Issues.

## Mode 1: One-off generation

```
/daily-comic owner/repo
/daily-comic owner/repo 2026-02-20
```

### Steps

1. **Check prerequisites**: Verify `GEMINI_API_KEY` is set. If not, stop and tell the user how to get one at https://aistudio.google.com/app/apikey

2. **Install dependencies** (if needed):
```bash
pip install google-genai Pillow requests 2>/dev/null
```

3. **Run the generator**:
```bash
TARGET_REPO="owner/repo" python scripts/daily_comic.py [date]
```

If `scripts/daily_comic.py` doesn't exist in the current directory, clone it from the bot repo first:
```bash
TMPDIR=$(mktemp -d)
git clone --depth 1 https://github.com/shalomer/github-comic-bot.git "$TMPDIR"
TARGET_REPO="owner/repo" GEMINI_API_KEY="$GEMINI_API_KEY" python "$TMPDIR/scripts/daily_comic.py" [date]
```

4. **Show the user** where the comic was saved and the panel titles/dialogue.

## Mode 2: Automated setup

```
/daily-comic setup owner/repo
```

Sets up daily comic delivery as GitHub Issues. The user's fork of `github-comic-bot` runs a daily Action that generates a comic from `owner/repo`'s commits and posts it as an Issue.

### Steps

1. **Check gh auth**:
```bash
gh auth status
```
If not logged in, tell the user to run `gh auth login` first and stop.

2. **Get Gemini API key**: Check if `GEMINI_API_KEY` is set in the environment. If not, ask the user for it. Tell them to get a free key at https://aistudio.google.com/app/apikey

3. **Fork the bot repo**:
```bash
gh repo fork shalomer/github-comic-bot --clone=false
```
Capture the fork name from the output (it will be `{username}/github-comic-bot`).

4. **Get the user's GitHub username**:
```bash
gh api user --jq '.login'
```

5. **Set the Gemini API key as a secret**:
```bash
gh secret set GEMINI_API_KEY --repo {username}/github-comic-bot --body "$GEMINI_API_KEY"
```

6. **Set the target repo as a variable**:
```bash
gh variable set TARGET_REPO --repo {username}/github-comic-bot --body "owner/repo"
```

7. **Check if target repo is private**:
```bash
gh repo view owner/repo --json isPrivate --jq '.isPrivate'
```
If private, the workflow needs a PAT to read commits. Set it:
```bash
GH_PAT=$(gh auth token)
gh secret set GH_PAT --repo {username}/github-comic-bot --body "$GH_PAT"
```
If public, skip this step (the default `GITHUB_TOKEN` can read public repos).

8. **Enable GitHub Actions on the fork**:
```bash
gh api repos/{username}/github-comic-bot/actions/permissions -X PUT -f enabled=true -f allowed_actions=all
```

9. **Trigger the first run**:
```bash
gh workflow run daily-comic.yml --repo {username}/github-comic-bot
```

10. **Tell the user**:
> Done! Your fork `{username}/github-comic-bot` is set up.
>
> - Daily comics will be generated from `owner/repo` commits
> - Each comic is posted as a GitHub Issue — you'll get notified via GitHub notifications
> - Schedule: every day at 6:00 AM IST (00:30 UTC)
> - First run triggered — check the Actions tab: https://github.com/{username}/github-comic-bot/actions
>
> To stop: disable the workflow in the Actions tab, or delete the fork.

## Important

- Always use `gh` CLI for GitHub operations (never raw API calls with curl)
- The fork inherits the workflow file — no need to create it
- `GITHUB_TOKEN` (the default Actions token) has issue write permission on the fork
- `GH_PAT` is only needed if the target repo is private
- If the fork already exists, `gh repo fork` will succeed (it's idempotent)
