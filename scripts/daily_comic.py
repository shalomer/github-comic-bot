#!/usr/bin/env python3
"""
Daily Comic Strip Generator

Fetches yesterday's commits from a GitHub repo, uses Gemini to write a
4-panel comic script (medieval RPG style), generates images with Gemini,
stitches them horizontally, and saves/opens the result.

Only requires a single GEMINI_API_KEY.
"""

import argparse
import json
import os
import sys
import base64
import platform
import subprocess
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import requests
from google import genai
from google.genai import types
from PIL import Image


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

TARGET_REPO = os.environ.get("TARGET_REPO", "shalomer/social-confidence-coach-v2")
COMIC_DIR = Path(__file__).resolve().parent.parent / "comic-strips"

GEMINI_TEXT_MODEL = "gemini-2.0-flash"
GEMINI_IMAGE_MODEL = "gemini-2.0-flash-exp-image-generation"

IMAGE_STYLE_PREFIX = (
    "Cartoon style, warm tones (coral, gold, cream), bold outlines, "
    "simple and clear, medieval fantasy village setting. "
)

# ---------------------------------------------------------------------------
# Step 1: Fetch commits
# ---------------------------------------------------------------------------

def fetch_commits(repo: str, date: Optional[str] = None) -> list[dict]:
    """Fetch commits from GitHub API for a given date (YYYY-MM-DD).

    If date is None, uses yesterday. Returns list of {sha, message, author}.
    """
    if date is None:
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        date = yesterday.strftime("%Y-%m-%d")

    since = f"{date}T00:00:00Z"
    until_date = datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1)
    until = until_date.strftime("%Y-%m-%dT00:00:00Z")

    url = f"https://api.github.com/repos/{repo}/commits"
    headers = {"Accept": "application/vnd.github+json"}

    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    commits = []
    page = 1
    while True:
        resp = requests.get(
            url,
            headers=headers,
            params={"since": since, "until": until, "per_page": 100, "page": page},
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        commits.extend(batch)
        if len(batch) < 100:
            break
        page += 1

    # Filter out merge commits, extract essentials
    results = []
    for c in commits:
        msg = c["commit"]["message"].split("\n")[0]  # first line only
        if msg.startswith("Merge pull request") or msg.startswith("Merge branch"):
            continue
        results.append({
            "sha": c["sha"][:7],
            "message": msg,
            "author": c["commit"]["author"]["name"],
        })

    return results


# ---------------------------------------------------------------------------
# Step 2: Generate comic script via Gemini
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are a comedy writer for a daily comic strip about GitHub commits.

SETTING: A medieval fantasy kingdom where a calm, deadpan knight (the developer) \
fixes bugs and builds features. The villagers (users) react with absurd, over-the-top \
emotions to every change — tiny fixes cause weeping, statues, parades; big features \
cause existential crises of joy.

YOUR JOB: Given a list of git commits, create a 4-panel comic script.

RULES:
- Panels 1-3: Pick the 3 funniest/most interesting commits. One commit per panel.
- Panel 4: Summary panel (total commits, key stats). Knight exhausted, villagers building statues or naming children.
- Each panel has: title (the actual commit message or a short version), scene (visual description for image generation), bubbles (2-3 short speech bubbles).
- Knight is ALWAYS calm, deadpan, slightly annoyed by gratitude. Says technical truths in 1-2 sentences.
- Villagers ALWAYS losing their minds. Crying, building monuments, naming children after git commands.
- Humor = exaggeration. The gap between how tiny the fix is and how massive the reaction is.
- 5th grader language. No fancy words. No narration boxes — only speech bubbles.
- Scene descriptions should be vivid and specific enough for image generation. Include character positions, expressions, and key visual elements.
- Personify bugs as monsters/ghosts/creatures when possible.
- Reference actual technical details (variable names, line counts, etc.) for punchlines.

OUTPUT FORMAT: Return ONLY a JSON array with exactly 4 objects:
[
  {
    "title": "commit message or short summary",
    "scene": "detailed visual scene description for image generation",
    "bubbles": [
      {"speaker": "Villager", "text": "..."},
      {"speaker": "Knight", "text": "..."}
    ]
  },
  ...
]

EXAMPLES OF GREAT PANELS:

Example 1 (from a "Step 3 of 2" off-by-one bug fix):
{
  "title": "Fix: \\"Step 3 of 2\\" onboarding bug",
  "scene": "Giant two-headed monster towering over a village. One head screams 'STEP 3!' the other screams 'OF 2!' Knight cuts it down with one calm swing of his sword.",
  "bubbles": [
    {"speaker": "Villager", "text": "He fixed the counter! Our children will learn to count again!"},
    {"speaker": "Knight", "text": "It was an off-by-one error."}
  ]
}

Example 2 (from deleting 14 test routes & 6 old landing pages):
{
  "title": "Delete 14 test routes & 6 old landing pages",
  "scene": "Knight casually pushes over 20 buildings like dominoes. Massive dust cloud rises behind him. Villagers watch from a safe distance.",
  "bubbles": [
    {"speaker": "Villager", "text": "He destroyed twenty buildings and the kingdom got FASTER!"},
    {"speaker": "Other villager", "text": "I lived in landing-v3..."},
    {"speaker": "Knight", "text": "Nobody lived in landing-v3."}
  ]
}

Example 3 (from a mobile calls freezing bug — 6 characters changed):
{
  "title": "Fix: mobile calls stuck after first message",
  "scene": "A massive ghost labeled '=== final' haunts an entire village, freezing everyone in place. Knight crosses out 6 characters on a tiny scroll and writes 6 new ones. Ghost explodes into sparkles.",
  "bubbles": [
    {"speaker": "Villager", "text": "The curse is lifted! Our phones work again!"},
    {"speaker": "Knight", "text": "I changed six characters."}
  ]
}

Example 4 (summary panel):
{
  "title": "40 commits. 8 bugs. 15 features. 17 demolished.",
  "scene": "Knight sitting exhausted in a wooden chair. In the background, villagers are building a golden statue of the knight. One villager is chiseling the face.",
  "bubbles": [
    {"speaker": "Villager", "text": "We shall name our firstborn git-push!"},
    {"speaker": "Knight", "text": "...it was just a Tuesday."}
  ]
}

Example 5 (navbar redesign — 384 lines):
{
  "title": "Redesign navbar: 384 lines added, 99 removed",
  "scene": "Villagers WEEPING with joy in front of a new shiny golden navigation bar mounted above the village gate. Flowers being thrown. One villager on his knees.",
  "bubbles": [
    {"speaker": "Villager", "text": "The tabs... they ANIMATE now!"},
    {"speaker": "Other villager", "text": "My grandfather died never seeing a floating pill nav."},
    {"speaker": "Knight", "text": "It's a menu bar."}
  ]
}
"""


def generate_script(commits: list[dict], api_key: str) -> list[dict]:
    """Use Gemini to generate a 4-panel comic script from commits."""
    client = genai.Client(api_key=api_key)

    commit_list = "\n".join(
        f"- [{c['sha']}] {c['message']}" for c in commits
    )
    user_msg = (
        f"Here are today's {len(commits)} commits:\n\n{commit_list}\n\n"
        f"Create a 4-panel comic strip. Return ONLY the JSON array."
    )

    response = client.models.generate_content(
        model=GEMINI_TEXT_MODEL,
        contents=user_msg,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
        ),
    )

    text = response.text.strip()

    # Strip markdown code fences if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]
        text = text.strip()

    panels = json.loads(text)
    assert isinstance(panels, list) and len(panels) == 4, f"Expected 4 panels, got {len(panels)}"
    return panels


# ---------------------------------------------------------------------------
# Step 3: Generate panel images via Gemini
# ---------------------------------------------------------------------------

def generate_panel_image(panel: dict, output_path: Path, api_key: str) -> bool:
    """Generate a single panel image using Gemini."""
    client = genai.Client(api_key=api_key)

    # Build the full prompt
    bubble_text = " ".join(
        f'{b["speaker"]}: "{b["text"]}"' for b in panel["bubbles"]
    )
    prompt = (
        f"{IMAGE_STYLE_PREFIX}"
        f"TOP TITLE BAR (black bar with white bold text): '{panel['title']}'. "
        f"{panel['scene']} "
        f"Speech bubbles: {bubble_text}"
    )

    print(f"  Generating: {panel['title'][:60]}...")

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=GEMINI_IMAGE_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                ),
            )

            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    image_data = part.inline_data.data
                    if isinstance(image_data, str):
                        image_data = base64.b64decode(image_data)
                    output_path.write_bytes(image_data)
                    print(f"  Saved: {output_path.name}")
                    return True

            print(f"  No image in response (attempt {attempt + 1})")
        except Exception as e:
            print(f"  Error (attempt {attempt + 1}): {e}")

        if attempt < max_retries - 1:
            time.sleep(5)

    return False


def generate_all_panels(panels: list[dict], tmp_dir: Path, api_key: str) -> list[Path]:
    """Generate images for all 4 panels. Returns list of image paths."""
    paths = []
    for i, panel in enumerate(panels):
        output = tmp_dir / f"panel_{i + 1}.png"
        success = generate_panel_image(panel, output, api_key)
        if not success:
            print(f"  FAILED to generate panel {i + 1}, skipping")
            continue
        paths.append(output)
        # Small delay between requests to avoid rate limits
        if i < len(panels) - 1:
            time.sleep(2)
    return paths


# ---------------------------------------------------------------------------
# Step 4: Stitch panels horizontally
# ---------------------------------------------------------------------------

def stitch_panels(panel_paths: list[Path], output_path: Path, gap: int = 20) -> Path:
    """Stitch panel images horizontally with a gap between them."""
    images = [Image.open(p) for p in panel_paths]

    # Normalize to same height (use the max height)
    max_height = max(img.height for img in images)
    resized = []
    for img in images:
        if img.height != max_height:
            ratio = max_height / img.height
            new_width = int(img.width * ratio)
            img = img.resize((new_width, max_height), Image.LANCZOS)
        resized.append(img)

    total_width = sum(img.width for img in resized) + gap * (len(resized) - 1)
    canvas = Image.new("RGB", (total_width, max_height), (255, 255, 255))

    x = 0
    for img in resized:
        canvas.paste(img, (x, 0))
        x += img.width + gap

    canvas.save(output_path, "PNG")
    print(f"Stitched {len(resized)} panels -> {output_path}")
    return output_path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def open_file(path: Path):
    """Open a file with the system default viewer."""
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.run(["open", str(path)], check=True)
        elif system == "Linux":
            subprocess.run(["xdg-open", str(path)], check=True)
        elif system == "Windows":
            os.startfile(str(path))
    except Exception:
        pass  # Don't fail if open doesn't work (e.g. headless CI)


def upload_image_as_release(image_path: Path, date: str) -> Optional[str]:
    """Compress PNG to JPEG and upload as a GitHub Release asset.

    Returns the release asset download URL, which renders in issue markdown
    for anyone with repo access (works for private repos).
    """
    # Compress PNG to JPEG
    jpeg_path = image_path.with_suffix(".jpg")
    try:
        img = Image.open(image_path)
        img.convert("RGB").save(jpeg_path, "JPEG", quality=85)
        print(f"  Compressed {image_path.name} -> {jpeg_path.name} "
              f"({jpeg_path.stat().st_size / 1024 / 1024:.1f}MB)")
    except Exception as e:
        print(f"  Compression failed: {e}")
        return None

    tag = f"comic-{date}"

    # Create release and upload asset via gh CLI
    try:
        result = subprocess.run(
            ["gh", "release", "create", tag, str(jpeg_path),
             "--title", f"Daily Comic {date}",
             "--notes", f"Auto-generated comic strip for {date}"],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            print(f"  Release creation failed: {result.stderr.strip()}")
            return None

        # Get the asset download URL
        result = subprocess.run(
            ["gh", "release", "view", tag, "--json", "assets",
             "--jq", ".assets[0].url"],
            capture_output=True, text=True, check=True,
        )
        asset_url = result.stdout.strip()
        if asset_url:
            print(f"  Release asset URL: {asset_url}")
            return asset_url
    except Exception as e:
        print(f"  Release upload error: {e}")

    return None


def create_github_issue(date: str, panels: list[dict], commits: list[dict]):
    """Create a GitHub Issue with the comic image and panel dialogue."""
    gh_repo = os.environ.get("GITHUB_REPOSITORY", "")
    if not gh_repo:
        print("WARNING: GITHUB_REPOSITORY not set, skipping issue creation")
        return

    # Upload image as release asset (works for private repos)
    image_path = COMIC_DIR / f"{date}.png"
    image_url = None
    if image_path.exists():
        print("Uploading comic image as release asset...")
        image_url = upload_image_as_release(image_path, date)

    # Fallback to raw.githubusercontent.com (only works for public repos)
    if not image_url:
        print("  Falling back to raw.githubusercontent.com URL")
        image_url = f"https://raw.githubusercontent.com/{gh_repo}/main/comic-strips/{date}.png"

    # Build the issue body
    body_lines = [
        f"![Daily Comic — {date}]({image_url})",
        "",
        "---",
        "",
    ]

    for i, panel in enumerate(panels):
        body_lines.append(f"### Panel {i + 1}: {panel['title']}")
        for bubble in panel.get("bubbles", []):
            body_lines.append(f"> **{bubble['speaker']}**: {bubble['text']}")
        body_lines.append("")

    body_lines.extend([
        "---",
        f"*{len(commits)} commits summarized into 4 panels.*",
    ])

    title = f"Daily Comic — {date} — {len(commits)} commits"
    body = "\n".join(body_lines)

    try:
        subprocess.run(
            ["gh", "issue", "create", "--title", title, "--body", body],
            check=True,
        )
        print(f"Created GitHub Issue: {title}")
    except FileNotFoundError:
        print("WARNING: gh CLI not found, skipping issue creation")
    except subprocess.CalledProcessError as e:
        print(f"WARNING: Failed to create issue: {e}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Daily Comic Strip Generator")
    parser.add_argument("date", nargs="?", default=None, help="Date in YYYY-MM-DD format (defaults to yesterday)")
    parser.add_argument("--create-issue", action="store_true", help="Create a GitHub Issue from saved JSON (run after commit+push)")
    args = parser.parse_args()

    date = args.date
    if date is None:
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        date = yesterday.strftime("%Y-%m-%d")

    # --create-issue: read from saved JSON, create issue, and exit
    if args.create_issue:
        script_path = COMIC_DIR / f"{date}.json"
        if not script_path.exists():
            print(f"No comic JSON found for {date}, skipping issue creation")
            sys.exit(0)
        with open(script_path) as f:
            data = json.load(f)
        create_github_issue(data["date"], data["panels"], data["commits"])
        sys.exit(0)

    print(f"=== Daily Comic Generator — {date} ===\n")

    # Required env vars
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        print("ERROR: GEMINI_API_KEY not set")
        print("Get one free at https://aistudio.google.com/app/apikey")
        sys.exit(1)

    repo = os.environ.get("TARGET_REPO", TARGET_REPO)

    # Step 1: Fetch commits
    print(f"[1/4] Fetching commits from {repo}...")
    commits = fetch_commits(repo, date)
    print(f"  Found {len(commits)} commits\n")

    if not commits:
        print("No commits yesterday. No comic today.")
        sys.exit(0)

    for c in commits:
        print(f"  {c['sha']} {c['message']}")
    print()

    # Step 2: Generate script
    print("[2/4] Generating comic script via Gemini...")
    panels = generate_script(commits, gemini_key)
    print(f"  Generated {len(panels)} panels:")
    for i, p in enumerate(panels):
        print(f"  Panel {i+1}: {p['title']}")
    print()

    # Step 3: Generate images
    print("[3/4] Generating panel images via Gemini...")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        panel_paths = generate_all_panels(panels, tmp_dir, gemini_key)

        if len(panel_paths) < 2:
            print("ERROR: Fewer than 2 panels generated. Aborting.")
            sys.exit(1)
        print()

        # Step 4: Stitch
        print("[4/4] Stitching panels...")
        COMIC_DIR.mkdir(parents=True, exist_ok=True)
        output_path = COMIC_DIR / f"{date}.png"
        stitch_panels(panel_paths, output_path)
        print()

    # Save script alongside image for reference
    script_path = COMIC_DIR / f"{date}.json"
    with open(script_path, "w") as f:
        json.dump({"date": date, "commits": commits, "panels": panels}, f, indent=2)
    print(f"Saved script: {script_path}")

    print(f"\nDone! Comic saved to {output_path}")
    open_file(output_path)


if __name__ == "__main__":
    main()
