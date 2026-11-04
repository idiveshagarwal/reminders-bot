# Roadmap — from Telegram bot to a Play Store / App Store app

Working name for the app: **Yaad** (याद — "remember"). Reminders and habits that speak your
language, live where you already chat, and look after your family too.

## What the best apps do well (teardown, Nov 2026)

| App | What it is perfect at | What it misses |
| --- | --- | --- |
| Apple Reminders | Siri + location reminders, smart lists, grocery auto-sort, shared lists | Apple-only; no habits or streaks |
| TickTick | Tasks + habit tracker + Pomodoro + calendar + Eisenhower matrix, quick-add dates | Busy UI; paid for the good parts |
| Todoist | Best natural-language quick add, filters, Karma points, integrations | Weak habits; English-first parsing |
| Google Tasks | Free, inside Gmail and Calendar | Very basic — no habits, few repeat rules |
| Microsoft To Do | "My Day" planning ritual, Outlook flagged emails | No habits, slow innovation |
| Any.do | WhatsApp reminders, daily planner, family and grocery lists | Paywall for WhatsApp; habits are an add-on |
| Things 3 | Design craft — Today / This Evening, calm UI | Apple-only, no collaboration |
| Habitica | Turns habits into an RPG with party accountability | Feels like a game first, planner second |
| Streaks | Simple habit rings, Apple Health links | iOS-only, habits only |

## Where Yaad can be different

1. **Chat-first in Hindi, Hinglish and English** — "kal subah 7 baje papa ko dawai yaad dilana" just works, by text or voice note.
2. **Telegram + WhatsApp first, app second** — no install needed to start; the app adds widgets and offline use.
3. **Family care** — a parent's medicine or BP check that is missed escalates to a son or daughter after 30 minutes.
4. **Indian calendar built in** — tithi, Ekadashi, festivals, EMI and bill dates, school fees, rent.
5. **Habits + reminders + streaks in one place**, with a streak-freeze day and an accountability buddy who sees your streak.
6. **Priced for India** — generous free tier; ₹49/month premium, ₹99/month family plan.

## Phases

### Phase 0 — make the bot correct (now)
- [ ] Real scheduled reminders with python-telegram-bot `JobQueue` (today they are only a list)
- [ ] Natural-language dates (`dateparser`, incl. Hindi) instead of splitting on "—"
- [ ] Stable ids (`uuid4`), not `hash()` (changes every run)
- [ ] SQLite / Postgres instead of `data.json` (lost on every redeploy on Railway/Render)
- [ ] Fix: `toggle_habit` answers the callback twice; milestone message is built but never sent
- [ ] Fix: "30-day rate" divides all-time completions by 30
- [ ] `/help`, `/stop` (owner only), `/export`
- [ ] Tests + GitHub Actions; deploy on Railway/Render with a persistent volume

### Phase 1 — a reminders app people keep
- Recurring rules (daily / weekdays / monthly / yearly), snooze, lists actually used
- Habit reminders at a chosen time, weekly report, streak freeze

### Phase 2 — the Yaad difference
- WhatsApp Cloud API channel · voice notes (speech-to-text, Hindi)
- Family sharing with caregiver escalation · Panchang and festival calendar

### Phase 3 — mobile apps
- Flutter (one code base for Android + iOS), offline-first sync, home-screen widgets
- Play Store first (most Indian users), then App Store

### Phase 4 — sustainable
- Premium and family plans, referral rewards, privacy-first analytics
