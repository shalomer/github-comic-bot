# GitHub Comic Bot — Multi-Tenant SaaS Architecture

## Context
We built `github-comic-bot` as a single-user pipeline (GitHub Actions → OpenAI → Gemini → Telegram). This doc explores how it becomes a service other GitHub users can subscribe to.

## How It Would Work (User's Perspective)

1. User visits **gitcomics.dev** (or similar)
2. Signs in with GitHub OAuth
3. Picks a repo (or multiple repos) to track
4. Chooses delivery channel: Telegram, Discord, Slack, or email
5. Optionally customizes: comic style, character names, schedule, timezone
6. Gets a daily comic strip in their chosen channel every morning

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    Frontend                          │
│         Next.js / React app on Vercel                │
│   - Landing page, GitHub OAuth, dashboard            │
│   - Repo picker, delivery config, comic archive      │
└─────────────┬───────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────┐
│                    Backend API                        │
│            Vercel Serverless / Next.js API            │
│   - /api/auth (GitHub OAuth)                         │
│   - /api/repos (list user repos via GitHub token)    │
│   - /api/subscriptions (CRUD)                        │
│   - /api/webhooks/stripe (billing)                   │
└─────────────┬───────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────┐
│                    Database                           │
│                  Supabase (Postgres)                  │
│   - users (github_id, token, plan, timezone)         │
│   - subscriptions (repo, delivery_channel, style)    │
│   - comics (date, repo, image_url, script_json)      │
│   - delivery_log (sent_at, channel, status)          │
└─────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────┐
│              Scheduled Worker (Daily)                 │
│                                                      │
│   Option A: GitHub Actions cron (free, simple)       │
│   Option B: Vercel Cron / AWS Lambda (more control)  │
│   Option C: Railway / Render background worker       │
│                                                      │
│   For each active subscription:                      │
│     1. Fetch commits via GitHub API (user's token)   │
│     2. Generate script via OpenAI                    │
│     3. Generate images via Gemini                    │
│     4. Stitch with Pillow                            │
│     5. Upload to R2/S3                               │
│     6. Deliver via Telegram/Discord/Slack/Email      │
│     7. Log result                                    │
└─────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────┐
│              Image Storage                           │
│         Cloudflare R2 or S3 bucket                   │
│   - comic-strips/{user_id}/{date}.png                │
│   - Public URLs for web archive view                 │
└─────────────────────────────────────────────────────┘
```

---

## Key Architecture Decisions

### 1. Single Pipeline → Job Queue
**Current**: One GitHub Actions cron runs one pipeline.
**Multi-tenant**: Need to process N subscriptions per day.

- **< 100 users**: Simple loop in a single cron job. Process sequentially. GitHub Actions still works.
- **100–1000 users**: Job queue (BullMQ + Redis, or SQS). Worker pulls jobs, processes in parallel. Needed because Gemini rate limits + each comic takes ~30-45s.
- **1000+ users**: Multiple workers, priority queue (paying users first), retry logic.

### 2. Auth: GitHub OAuth
- User signs in with GitHub → we get an OAuth token with `repo` read scope
- Token stored encrypted in DB
- Used to fetch commits from their private repos (no PAT needed)
- Refresh token flow for long-lived access

### 3. Image Storage
- **Current**: Committed to git repo (doesn't scale)
- **Multi-tenant**: Upload to Cloudflare R2 (cheap, S3-compatible) or Supabase Storage
- Public URL per comic for web archive + Telegram delivery
- CDN in front for fast loading

### 4. Delivery Channels
| Channel | Implementation |
|---------|---------------|
| Telegram | Bot API `sendPhoto` (current approach, works great) |
| Discord | Webhook URL — user provides it, we POST to it |
| Slack | Slack App + incoming webhook |
| Email | Resend or SendGrid — attach image + HTML preview |

Each channel is a simple adapter: `send(image_url, caption, config)`.

### 5. Customization Levers
- **Schedule**: daily, weekdays only, weekly digest
- **Timezone**: determines "yesterday" for commit fetching
- **Style**: "medieval RPG" (default), "sci-fi", "office comedy", "anime" — just swaps the system prompt
- **Character names**: "The Knight" → custom name
- **Multi-repo**: combine commits from 2-3 repos into one strip

---

## Monetization

| Tier | Price | What You Get |
|------|-------|-------------|
| Free | $0 | 1 public repo, Telegram only, medieval style, 5 comics then paywall |
| Pro | $5/mo | Unlimited repos (public + private), all channels, all styles |
| Team | $15/mo | Shared team channel, multi-repo digests, priority processing |

**Unit economics** per comic:
- OpenAI GPT-4o: ~$0.01-0.03
- Gemini image gen: free (for now)
- Storage: ~$0.001
- Delivery: free (Telegram/Discord) or ~$0.001 (email)
- **Total: ~$0.03/comic → $0.90/mo per daily user**
- At $5/mo that's ~5.5x margin

---

## What Changes From Current Setup

| Aspect | Now (single-user) | Service |
|--------|--------------------|---------|
| Auth | None | GitHub OAuth |
| Config | Env vars | DB per subscription |
| Scheduling | GitHub Actions cron | Job queue + worker |
| Commits | One hardcoded repo | User's repos via their token |
| Images | Git commit | R2/S3 bucket |
| Delivery | One Telegram chat | Per-user channel config |
| Script gen | One system prompt | Templated per style |
| Billing | None | Stripe |
| Frontend | None | Dashboard + archive |

---

## Tech Stack (if building it)

- **Frontend**: Next.js on Vercel (reuse vibeCoach patterns)
- **Backend**: Next.js API routes + Vercel Cron (or separate worker)
- **DB**: Supabase (Postgres + auth + storage)
- **Queue**: BullMQ + Upstash Redis (only if > 100 users)
- **Storage**: Cloudflare R2
- **Billing**: Stripe Checkout + webhooks
- **AI**: OpenAI (script) + Gemini (images)
- **Delivery**: Telegram Bot API, Discord webhooks, Resend (email)

---

## Build Order (if you ever decide to build it)

1. **Landing page + waitlist** — gauge demand before building
2. **GitHub OAuth + repo picker + Telegram delivery** — MVP, manually triggered
3. **Daily cron + Stripe billing** — monetize
4. **Discord/Slack/Email channels** — expand reach
5. **Style customization + multi-repo** — differentiation
6. **Team features** — upsell
