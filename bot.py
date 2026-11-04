import os
import json
import logging
from datetime import date, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_FILE = "data.json"

WAITING_REMINDER = 1
WAITING_HABIT_NAME = 2
WAITING_HABIT_COLOR = 3

HABIT_COLORS = ["🔴", "🟠", "🟡", "🟢", "🔵", "🟣"]

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_user(data, uid):
    uid = str(uid)
    if uid not in data:
        data[uid] = {
            "reminders": [],
            "habits": [],
            "lists": [
                {"id": "personal", "name": "Personal", "emoji": "👤"},
                {"id": "work",     "name": "Work",     "emoji": "💼"},
                {"id": "shopping", "name": "Shopping", "emoji": "🛒"},
            ]
        }
    return data[uid]

def today_str():
    return date.today().isoformat()

def calc_streak(completions):
    streak = 0
    check_date = date.today()
    if today_str() not in completions:
        check_date -= timedelta(days=1)
    while check_date.isoformat() in completions:
        streak += 1
        check_date -= timedelta(days=1)
    return streak

def calc_best_streak(completions):
    if not completions:
        return 0
    dates = sorted(completions)
    best = cur = 1
    for i in range(1, len(dates)):
        d1 = date.fromisoformat(dates[i-1])
        d2 = date.fromisoformat(dates[i])
        if (d2 - d1).days == 1:
            cur += 1
            best = max(best, cur)
        else:
            cur = 1
    return best

def build_heatmap(completions):
    cells = []
    for i in range(27, -1, -1):
        d = (date.today() - timedelta(days=i)).isoformat()
        cells.append("🟩" if d in completions else "⬜")
    rows = []
    for i in range(0, 28, 7):
        rows.append("".join(cells[i:i+7]))
    return "\n".join(rows)

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    get_user(data, update.effective_user.id)
    save_data(data)
    kb = [
        [InlineKeyboardButton("📋 My reminders", callback_data="view_reminders"),
         InlineKeyboardButton("🔥 Habit tracker", callback_data="view_habits")],
        [InlineKeyboardButton("➕ Add reminder", callback_data="add_reminder"),
         InlineKeyboardButton("➕ Add habit", callback_data="add_habit")],
    ]
    await update.message.reply_text(
        "👋 *Welcome to your Reminders Bot!*\n\nTrack reminders, build habits, and maintain streaks — all in Telegram.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb)
    )

async def show_home(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    kb = [
        [InlineKeyboardButton("📋 My reminders", callback_data="view_reminders"),
         InlineKeyboardButton("🔥 Habit tracker", callback_data="view_habits")],
        [InlineKeyboardButton("➕ Add reminder", callback_data="add_reminder"),
         InlineKeyboardButton("➕ Add habit", callback_data="add_habit")],
    ]
    await query.edit_message_text(
        "🏠 *Home*\n\nWhat would you like to do?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb)
    )

async def view_reminders(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = load_data()
    user = get_user(data, query.from_user.id)
    rems = user["reminders"]

    pending = [r for r in rems if not r.get("done")]
    done    = [r for r in rems if r.get("done")]

    text = "📋 *Your Reminders*\n\n"
    if not rems:
        text += "_No reminders yet. Add one!_"
    else:
        if pending:
            text += f"*Active ({len(pending)})*\n"
            for r in pending:
                date_str = f" — _{r['date']}_" if r.get("date") else ""
                text += f"• {r['text']}{date_str}\n"
        if done:
            text += f"\n*Completed ({len(done)})*\n"
            for r in done:
                text += f"~{r['text']}~\n"

    kb = []
    for r in pending:
        kb.append([
            InlineKeyboardButton(f"✅ {r['text'][:30]}", callback_data=f"done_rem_{r['id']}"),
            InlineKeyboardButton("🗑", callback_data=f"del_rem_{r['id']}")
        ])
    kb.append([
        InlineKeyboardButton("➕ Add reminder", callback_data="add_reminder"),
        InlineKeyboardButton("🏠 Home", callback_data="home")
    ])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

async def view_habits(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = load_data()
    user = get_user(data, query.from_user.id)
    habits = user["habits"]

    today = today_str()
    done_today = sum(1 for h in habits if today in h.get("completions", []))

    text = "🔥 *Habit Tracker*\n"
    if habits:
        text += f"_Today: {done_today}/{len(habits)} done_\n\n"
    else:
        text += "\n_No habits yet. Add one!_\n"

    kb = []
    for h in habits:
        streak = calc_streak(h.get("completions", []))
        is_done = today in h.get("completions", [])
        fire = "🔥" if streak >= 3 else ("✅" if is_done else "⭕")
        label = f"{h.get('emoji','🎯')} {h['name']} — {streak}d streak {fire}"
        cb = f"undone_habit_{h['id']}" if is_done else f"done_habit_{h['id']}"
        btn_label = "↩️ Undo" if is_done else "✅ Done"
        kb.append([
            InlineKeyboardButton(label[:40], callback_data=f"habit_detail_{h['id']}"),
            InlineKeyboardButton(btn_label, callback_data=cb)
        ])

    kb.append([
        InlineKeyboardButton("➕ Add habit", callback_data="add_habit"),
        InlineKeyboardButton("🏠 Home", callback_data="home")
    ])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

async def habit_detail(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    habit_id = query.data.replace("habit_detail_", "")
    data = load_data()
    user = get_user(data, query.from_user.id)
    h = next((x for x in user["habits"] if x["id"] == habit_id), None)
    if not h:
        await query.answer("Habit not found.", show_alert=True)
        return

    completions = h.get("completions", [])
    streak = calc_streak(completions)
    best = calc_best_streak(completions)
    total = len(completions)
    today_date = date.today()
    recent_days = {(today_date - timedelta(days=i)).isoformat() for i in range(30)}
    rate = round(len(recent_days.intersection(completions)) / 30 * 100)
    heatmap = build_heatmap(completions)
    today = today_str()
    is_done = today in completions

    text = (
        f"{h.get('emoji','🎯')} *{h['name']}*\n\n"
        f"🔥 Current streak: *{streak} days*\n"
        f"🏆 Best streak: *{best} days*\n"
        f"✅ Total done: *{total} times*\n"
        f"📊 30-day rate: *{rate}%*\n\n"
        f"*Last 4 weeks*\n{heatmap}\n"
        f"⬜ = missed   🟩 = done"
    )
    done_btn = "↩️ Undo today" if is_done else "✅ Mark today done"
    done_cb = f"undone_habit_{habit_id}" if is_done else f"done_habit_{habit_id}"
    kb = [
        [InlineKeyboardButton(done_btn, callback_data=done_cb)],
        [InlineKeyboardButton("🗑 Delete habit", callback_data=f"del_habit_{habit_id}"),
         InlineKeyboardButton("◀️ Back", callback_data="view_habits")]
    ]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))

async def toggle_habit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    marking_done = query.data.startswith("done_habit_")
    habit_id = query.data.replace("done_habit_", "").replace("undone_habit_", "")
    data = load_data()
    user = get_user(data, query.from_user.id)
    h = next((x for x in user["habits"] if x["id"] == habit_id), None)
    if not h:
        return
    if "completions" not in h:
        h["completions"] = []
    today = today_str()
    if marking_done and today not in h["completions"]:
        h["completions"].append(today)
        streak = calc_streak(h["completions"])
        msg = f"🔥 *{h['name']}* done for today!\nCurrent streak: *{streak} day{'s' if streak!=1 else ''}*"
        if streak == 7:  msg += "\n\n🏅 One week streak!"
        if streak == 30: msg += "\n\n🏆 30-day streak! Incredible!"
        await query.answer(f"Streak: {streak} days 🔥", show_alert=False)
    elif not marking_done and today in h["completions"]:
        h["completions"].remove(today)
        msg = f"↩️ *{h['name']}* unmarked for today."
        await query.answer("Unmarked", show_alert=False)
    else:
        return
    save_data(data)
    await view_habits(update, ctx)

async def toggle_reminder(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    rem_id = query.data.replace("done_rem_", "")
    data = load_data()
    user = get_user(data, query.from_user.id)
    for r in user["reminders"]:
        if r["id"] == rem_id:
            r["done"] = True
            break
    save_data(data)
    await view_reminders(update, ctx)

async def delete_reminder(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    rem_id = query.data.replace("del_rem_", "")
    data = load_data()
    user = get_user(data, query.from_user.id)
    user["reminders"] = [r for r in user["reminders"] if r["id"] != rem_id]
    save_data(data)
    await view_reminders(update, ctx)

async def delete_habit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    habit_id = query.data.replace("del_habit_", "")
    data = load_data()
    user = get_user(data, query.from_user.id)
    user["habits"] = [h for h in user["habits"] if h["id"] != habit_id]
    save_data(data)
    await view_habits(update, ctx)

async def start_add_reminder(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📝 *New Reminder*\n\nType your reminder text:\n_(e.g. 'Buy milk' or 'Call mom — Tomorrow')_",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="home")]])
    )
    return WAITING_REMINDER

async def receive_reminder(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    parts = text.split("—")
    name = parts[0].strip()
    date_hint = parts[1].strip() if len(parts) > 1 else None
    data = load_data()
    user = get_user(data, update.effective_user.id)
    rem = {"id": str(len(user["reminders"]) + 1) + str(hash(name))[-4:], "text": name, "done": False}
    if date_hint:
        rem["date"] = date_hint
    user["reminders"].append(rem)
    save_data(data)
    kb = [[InlineKeyboardButton("📋 View reminders", callback_data="view_reminders"),
           InlineKeyboardButton("🏠 Home", callback_data="home")]]
    await update.message.reply_text(
        f"✅ Reminder added!\n\n*{name}*" + (f"\n📅 {date_hint}" if date_hint else ""),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb)
    )
    return ConversationHandler.END

async def start_add_habit(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🎯 *New Habit*\n\nWhat habit do you want to build?\n_(e.g. 'Meditate', 'Exercise', 'Read')_",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="home")]])
    )
    return WAITING_HABIT_NAME

async def receive_habit_name(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["new_habit_name"] = update.message.text.strip()
    kb = [[InlineKeyboardButton(e, callback_data=f"pick_emoji_{e}") for e in HABIT_COLORS]]
    await update.message.reply_text(
        "Pick a color for your habit:",
        reply_markup=InlineKeyboardMarkup(kb)
    )
    return WAITING_HABIT_COLOR

async def receive_habit_color(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    emoji = query.data.replace("pick_emoji_", "")
    name = ctx.user_data.get("new_habit_name", "New habit")
    data = load_data()
    user = get_user(data, query.from_user.id)
    habit = {
        "id": "h" + str(len(user["habits"]) + 1) + str(hash(name))[-4:],
        "name": name,
        "emoji": emoji,
        "completions": []
    }
    user["habits"].append(habit)
    save_data(data)
    kb = [[InlineKeyboardButton("🔥 View habits", callback_data="view_habits"),
           InlineKeyboardButton("🏠 Home", callback_data="home")]]
    await query.edit_message_text(
        f"✅ Habit created!\n\n{emoji} *{name}*\n\nStart building your streak today!",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(kb)
    )
    return ConversationHandler.END

async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END

def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise ValueError("Set BOT_TOKEN environment variable")

    app = Application.builder().token(token).build()

    conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(start_add_reminder, pattern="^add_reminder$"),
            CallbackQueryHandler(start_add_habit, pattern="^add_habit$"),
        ],
        states={
            WAITING_REMINDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_reminder)],
            WAITING_HABIT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_habit_name)],
            WAITING_HABIT_COLOR: [CallbackQueryHandler(receive_habit_color, pattern="^pick_emoji_")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(show_home, pattern="^home$"))
    app.add_handler(CallbackQueryHandler(view_reminders, pattern="^view_reminders$"))
    app.add_handler(CallbackQueryHandler(view_habits, pattern="^view_habits$"))
    app.add_handler(CallbackQueryHandler(habit_detail, pattern="^habit_detail_"))
    app.add_handler(CallbackQueryHandler(toggle_habit, pattern="^done_habit_|^undone_habit_"))
    app.add_handler(CallbackQueryHandler(toggle_reminder, pattern="^done_rem_"))
    app.add_handler(CallbackQueryHandler(delete_reminder, pattern="^del_rem_"))
    app.add_handler(CallbackQueryHandler(delete_habit, pattern="^del_habit_"))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
