# Reminders & Habit Tracker — Telegram Bot

> **Status:** early prototype (June 2026) — the first project I built with Claude. It is being turned into **Yaad**, a reminders + habits app for India. See [ROADMAP.md](ROADMAP.md) for the plan and the known issues being fixed first.

A full-featured Telegram bot with reminders, habit tracking, streaks, and heatmaps.

## Features

- **Reminders** — add, complete, delete. Supports optional due dates.
- **Habit tracker** — daily check-ins with streak counting
- **Streak display** — current streak shown on every habit; milestone alerts at 7 and 30 days
- **Heatmap** — 4-week visual grid (🟩 done, ⬜ missed) per habit
- **Stats** — current streak, best streak, total completions, 30-day completion rate
- **Multi-user** — each Telegram user gets their own isolated data stored in `data.json`

---

## Setup (5 minutes)

### 1. Get a Bot Token

1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the prompts
3. Copy the token it gives you (looks like `123456:ABC-DEF...`)

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the bot

```bash
BOT_TOKEN="your_token_here" python bot.py
```

Or on Windows:
```cmd
set BOT_TOKEN=your_token_here
python bot.py
```

---

## Usage

| Command / Button | Action |
|---|---|
| `/start` | Open home menu |
| 📋 My reminders | View all reminders with complete/delete buttons |
| 🔥 Habit tracker | View habits with today's status and streaks |
| ➕ Add reminder | Type reminder text (add ` — Tomorrow` etc. for a date) |
| ➕ Add habit | Name your habit, pick a color emoji |
| Tap a habit name | See full stats + 4-week heatmap |
| ✅ Done / ↩️ Undo | Toggle today's habit completion |

---

## Deploy to a server (optional)

To keep it running 24/7:

### Using systemd (Linux VPS)

Create `/etc/systemd/system/reminders-bot.service`:

```ini
[Unit]
Description=Reminders Telegram Bot
After=network.target

[Service]
WorkingDirectory=/path/to/reminders_bot
ExecStart=/usr/bin/python3 bot.py
Environment=BOT_TOKEN=your_token_here
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable reminders-bot
sudo systemctl start reminders-bot
```

### Using Railway / Render / Fly.io

Set `BOT_TOKEN` as an environment variable in your project settings, then deploy the folder. These platforms offer free tiers.

---

## Data storage

All data is saved to `data.json` in the same folder. Each user's reminders and habits are stored by their Telegram user ID. Back this file up regularly if deploying to a server.

---

## Roadmap & known issues

See [ROADMAP.md](ROADMAP.md) and the [Issues](../../issues) tab.

## License

[MIT](LICENSE) © 2026 Divesh Agarwal

## Tests

Run the offline regression tests after installing the dependencies:

```bash
python -m unittest discover -s tests -v
```
