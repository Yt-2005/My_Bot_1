"""
Python 3.13/3.14 Compatibility Fix for python-telegram-bot
បំណែកប្រែសម្រួលសម្រាប់ Python 3.13+ — បន្ថែម slot ដែលបាត់បង់ក្នុង Updater class
Official fix reference: python-telegram-bot v21.0 — "Add Missing Slot to Updater"
"""
import sys

# ត្រួតពិនិត្យថាតើជា Python 3.13+ ឬអត់
if sys.version_info >= (3, 13):
    import telegram.ext._updater

    # បន្ថែម slot ដែលបាត់បង់ទៅក្នុង Updater class
    # នេះជាការកែប្រែផ្លូវការពី python-telegram-bot v21.0
    missing_slot = '_Updater__polling_cleanup_cb'
    if missing_slot not in telegram.ext._updater.Updater.__slots__:
        # បង្កើត class ថ្មីដែលមាន slot ពេញលេញ
        original_slots = list(telegram.ext._updater.Updater.__slots__)
        original_slots.append(missing_slot)
        telegram.ext._updater.Updater.__slots__ = tuple(original_slots)
        print("✅ បានបន្ថែម slot សម្រួល Python 3.13+ សម្រាប់ Updater")

import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv
load_dotenv()

from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)
from google import genai as google_genai

from database import (
    init_db, get_user, create_user, set_pin, get_pin,
    set_language, get_language, set_reminder, set_budget, get_budget,
    add_expense, delete_expense, get_today, get_by_date,
    get_monthly, get_monthly_total, get_by_tag, get_recurring,
    add_goal, get_goals, update_goal_savings
)
from translations import t

TOKEN      = os.environ.get("TOKEN", "")
GEMINI_KEY = os.environ.get("GEMINI_KEY", "")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

(
    PIN_VERIFY, PIN_SET, PIN_CONFIRM,
    CHOOSE_CAT, ENTER_AMOUNT, ENTER_NOTE, ENTER_TAG, IS_RECURRING, RECURRING_INT,
    ENTER_RECEIPT,
    GOAL_NAME, GOAL_TARGET, GOAL_DEADLINE,
    BUDGET_AMOUNT,
    REMINDER_TIME,
    SEARCH_DATE, SEARCH_TAG,
    DELETE_ID,
    LANG_CHOOSE,
) = range(19)

CATEGORIES = [
    ["🍜 អាហារ", "🚗 ប្រេង/ យាន"],
    ["🛒 ទំនិញ", "💊 ថ្នាំ/សុខភាព"],
    ["📱 ទូរស័ព្ទ", "🏠 ផ្ទះ/ទឹកភ្លើង"],
    ["🎮 កំសាន្ត", "✈️ ការធ្វើដំណើរ"],
    ["📚 ការសិក្សា", "👔 សម្លៀកបំពាក់"],
    ["📦 ផ្សេងៗ"],
]

authenticated_users = set()

# ---- Health Check Server for UptimeRobot ----
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")
    def log_message(self, format, *args):
        pass  # បិទ log

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

# ---- Helper functions ----
def is_authenticated(user_id):
    pin = get_pin(user_id)
    if not pin:
        return True
    return user_id in authenticated_users

def progress_bar(pct):
    filled = int(pct / 10)
    return "█" * filled + "░" * (10 - filled)

def common_fallbacks():
    return [
        CommandHandler("cancel",    cancel),
        CommandHandler("ai",        ai_advice),
        CommandHandler("today",     today),
        CommandHandler("month",     month),
        CommandHandler("compare",   compare),
        CommandHandler("recurring", recurring),
    ]

# ---- Handlers ----
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    create_user(uid)
    if not is_authenticated(uid):
        await update.message.reply_text(t(uid, 'pin_enter'))
        return PIN_VERIFY
    await update.message.reply_text(t(uid, 'welcome'))

async def pin_verify(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    entered = update.message.text.strip()
    if entered == get_pin(uid):
        authenticated_users.add(uid)
        await update.message.reply_text(t(uid, 'welcome'))
        return ConversationHandler.END
    else:
        await update.message.reply_text(t(uid, 'pin_wrong'))
        return PIN_VERIFY

async def setpin_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(t(uid, 'enter_pin'))
    return PIN_SET

async def pin_set_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    pin = update.message.text.strip()
    if not pin.isdigit() or len(pin) != 4:
        await update.message.reply_text("❌ PIN ត្រូវមាន 4 ខ្ទង់លេខ!")
        return PIN_SET
    set_pin(uid, pin)
    authenticated_users.add(uid)
    await update.message.reply_text(t(uid, 'pin_set'))
    return ConversationHandler.END

async def lang_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    kb = [["🇰🇭 ខ្មែរ", "🇬🇧 English"]]
    await update.message.reply_text(
        "🌐 ជ្រើសភាសា / Choose language:",
        reply_markup=ReplyKeyboardMarkup(kb, one_time_keyboard=True, resize_keyboard=True)
    )
    return LANG_CHOOSE

async def lang_choose(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    choice = update.message.text
    if "English" in choice:
        set_language(uid, 'en')
        await update.message.reply_text("✅ Language changed to English!")
    else:
        set_language(uid, 'km')
        await update.message.reply_text("✅ ប្តូរភាសាជា ខ្មែរ រួចហើយ!")
    return ConversationHandler.END

async def add_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_authenticated(uid):
        await update.message.reply_text(t(uid, 'pin_enter'))
        return PIN_VERIFY
    rm = ReplyKeyboardMarkup(CATEGORIES, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(t(uid, 'choose_cat'), reply_markup=rm)
    return CHOOSE_CAT

async def choose_category(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data['cat'] = update.message.text
    uid = update.effective_user.id
    await update.message.reply_text(t(uid, 'enter_amount'))
    return ENTER_AMOUNT

async def enter_amount(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    try:
        amount = float(update.message.text.replace(",", "").replace("$", ""))
        ctx.user_data['amount'] = amount
        await update.message.reply_text(t(uid, 'enter_note'))
        return ENTER_NOTE
    except ValueError:
        await update.message.reply_text(t(uid, 'invalid_amount'))
        return ENTER_AMOUNT

async def enter_note(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    ctx.user_data['note'] = update.message.text
    await update.message.reply_text(t(uid, 'enter_tag'))
    return ENTER_TAG

async def enter_tag(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    ctx.user_data['tag'] = update.message.text if update.message.text != '-' else ''
    kb = [[t(uid, 'yes'), t(uid, 'no')]]
    await update.message.reply_text(
        t(uid, 'is_recurring'),
        reply_markup=ReplyKeyboardMarkup(kb, one_time_keyboard=True, resize_keyboard=True)
    )
    return IS_RECURRING

async def is_recurring(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    is_rec = t(uid, 'yes') in update.message.text
    ctx.user_data['is_recurring'] = is_rec
    if is_rec:
        kb = [["📅 ប្រចាំថ្ងៃ", "📅 ប្រចាំសប្តាហ៍"], ["📅 ប្រចាំខែ"]]
        await update.message.reply_text(
            t(uid, 'recurring_interval'),
            reply_markup=ReplyKeyboardMarkup(kb, one_time_keyboard=True, resize_keyboard=True)
        )
        return RECURRING_INT
    return await save_expense(update, ctx, "")

async def recurring_interval(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data['rec_interval'] = update.message.text
    return await save_expense(update, ctx, update.message.text)

async def save_expense(update, ctx, interval):
    uid    = update.effective_user.id
    cat    = ctx.user_data['cat']
    amt    = ctx.user_data['amount']
    note   = ctx.user_data['note']
    tag    = ctx.user_data.get('tag', '')
    is_rec = ctx.user_data.get('is_recurring', False)
    add_expense(uid, cat, amt, note, tag, "", 1 if is_rec else 0, interval)
    await update.message.reply_text(t(uid, 'saved', cat=cat, amt=amt, note=note, tag=tag or "-"))
    budget = get_budget(uid)
    if budget > 0:
        used = get_monthly_total(uid)
        pct  = (used / budget) * 100
        if pct >= 100:
            await update.message.reply_text(t(uid, 'budget_exceeded', used=used, budget=budget))
        elif pct >= 80:
            await update.message.reply_text(t(uid, 'budget_warning', pct=pct, used=used, budget=budget))
    return ConversationHandler.END

async def today(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_authenticated(uid): return ConversationHandler.END
    rows = get_today(uid)
    if not rows:
        await update.message.reply_text(t(uid, 'no_expense'))
        return ConversationHandler.END
    total = sum(r[2] for r in rows)
    text  = t(uid, 'today_header')
    for eid, cat, amt, note, tag in rows:
        text += f"#{eid} {cat}: {amt:,.0f}"
        if note and note != '-': text += f" ({note})"
        if tag  and tag  != '-': text += f" 🏷️{tag}"
        text += "\n"
    text += t(uid, 'total', total=total)
    await update.message.reply_text(text)
    return ConversationHandler.END

async def month(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_authenticated(uid): return ConversationHandler.END
    ym   = datetime.now().strftime("%Y-%m")
    rows = get_monthly(uid)
    if not rows:
        await update.message.reply_text(t(uid, 'no_expense'))
        return ConversationHandler.END
    total = sum(r[1] for r in rows)
    text  = t(uid, 'month_header', month=ym)
    for cat, amt in rows:
        pct   = (amt / total * 100) if total else 0
        text += f"• {cat}: {amt:,.0f} ({pct:.0f}%)\n"
    text += t(uid, 'total', total=total)
    budget = get_budget(uid)
    if budget > 0:
        pct   = (total / budget) * 100
        text += f"\n\n📊 ថវិកា: {total:,.0f}/{budget:,.0f} ({pct:.0f}%)\n"
        text += progress_bar(min(pct, 100))
    await update.message.reply_text(text)
    return ConversationHandler.END

async def compare(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_authenticated(uid): return ConversationHandler.END
    now        = datetime.now()
    this_month = now.strftime("%Y-%m")
    last       = (now.replace(day=1) - timedelta(days=1))
    last_month = last.strftime("%Y-%m")
    this_total = get_monthly_total(uid, this_month)
    last_total = get_monthly_total(uid, last_month)
    diff  = this_total - last_total
    emoji = "📈" if diff > 0 else "📉"
    text  = t(uid, 'compare_header')
    text += f"• {last_month}: {last_total:,.0f}\n"
    text += f"• {this_month}: {this_total:,.0f}\n\n"
    text += f"{emoji} ផ្លាស់ប្តូរ: {abs(diff):,.0f} ({'ច្រើនជាង' if diff > 0 else 'តិចជាង'})"
    await update.message.reply_text(text)
    return ConversationHandler.END

async def date_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(t(uid, 'enter_date'))
    return SEARCH_DATE

async def date_search(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid      = update.effective_user.id
    date_str = update.message.text.strip()
    rows     = get_by_date(uid, date_str)
    if not rows:
        await update.message.reply_text(t(uid, 'no_expense'))
        return ConversationHandler.END
    total = sum(r[2] for r in rows)
    text  = f"📅 ចំណាយថ្ងៃ {date_str}:\n\n"
    for eid, cat, amt, note, tag in rows:
        text += f"#{eid} {cat}: {amt:,.0f}"
        if note and note != '-': text += f" ({note})"
        text += "\n"
    text += t(uid, 'total', total=total)
    await update.message.reply_text(text)
    return ConversationHandler.END

async def tags_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(t(uid, 'enter_tag_search'))
    return SEARCH_TAG

async def tag_search(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid  = update.effective_user.id
    tag  = update.message.text.strip()
    rows = get_by_tag(uid, tag)
    if not rows:
        await update.message.reply_text(t(uid, 'no_expense'))
        return ConversationHandler.END
    total = sum(r[2] for r in rows)
    text  = f"🏷️ Tag: {tag}\n\n"
    for eid, cat, amt, note, date in rows:
        text += f"• {date} {cat}: {amt:,.0f} ({note})\n"
    text += t(uid, 'total', total=total)
    await update.message.reply_text(text)
    return ConversationHandler.END

async def recurring(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid  = update.effective_user.id
    if not is_authenticated(uid): return ConversationHandler.END
    rows = get_recurring(uid)
    if not rows:
        await update.message.reply_text("📭 គ្មានចំណាយដដែលៗទេ!")
        return ConversationHandler.END
    text = "🔄 ចំណាយដដែលៗ:\n\n"
    for cat, amt, note, interval in rows:
        text += f"• {cat}: {amt:,.0f} ({interval})\n  📝 {note}\n"
    await update.message.reply_text(text)
    return ConversationHandler.END

async def goal_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    kb  = [["➕ បន្ថែមគោលដៅ", "📋 មើលគោលដៅ"]]
    await update.message.reply_text(
        "🎯 គោលដៅសន្សំ:",
        reply_markup=ReplyKeyboardMarkup(kb, one_time_keyboard=True, resize_keyboard=True)
    )
    return GOAL_NAME

async def goal_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if "មើល" in update.message.text:
        rows = get_goals(uid)
        if not rows:
            await update.message.reply_text("📭 គ្មានគោលដៅទេ!")
            return ConversationHandler.END
        text = t(uid, 'goals_header')
        for gid, name, target, saved, deadline in rows:
            pct = (saved / target * 100) if target else 0
            bar = progress_bar(min(pct, 100))
            text += t(uid, 'goal_progress', name=name, saved=saved,
                      target=target, pct=pct, bar=bar, deadline=deadline)
        await update.message.reply_text(text)
        return ConversationHandler.END
    await update.message.reply_text(t(uid, 'goal_name'))
    return GOAL_TARGET

async def goal_name(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data['goal_name'] = update.message.text
    uid = update.effective_user.id
    await update.message.reply_text(t(uid, 'goal_target'))
    return GOAL_DEADLINE

async def goal_target(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    try:
        ctx.user_data['goal_target'] = float(update.message.text.replace(",", ""))
        await update.message.reply_text(t(uid, 'goal_deadline'))
        return GOAL_DEADLINE + 1
    except:
        await update.message.reply_text(t(uid, 'invalid_amount'))
        return GOAL_DEADLINE

async def goal_deadline(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid      = update.effective_user.id
    name     = ctx.user_data['goal_name']
    target   = ctx.user_data['goal_target']
    deadline = update.message.text.strip()
    add_goal(uid, name, target, deadline)
    await update.message.reply_text(t(uid, 'goal_saved', name=name, target=target))
    return ConversationHandler.END

async def budget_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid     = update.effective_user.id
    current = get_budget(uid)
    await update.message.reply_text(f"💳 ថវិកាបច្ចុប្បន្ន: {current:,.0f}\n\n💵 បញ្ចូលថវិកាខែថ្មី:")
    return BUDGET_AMOUNT

async def budget_set(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    try:
        budget = float(update.message.text.replace(",", ""))
        set_budget(uid, budget)
        await update.message.reply_text(t(uid, 'budget_set', budget=budget))
    except:
        await update.message.reply_text(t(uid, 'invalid_amount'))
    return ConversationHandler.END

async def reminder_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    kb  = [
        ["⏰ ម៉ោង 8:00",  "⏰ ម៉ោង 12:00"],
        ["⏰ ម៉ោង 18:00", "⏰ ម៉ោង 20:00"],
        ["❌ បិទការរំលឹក"]
    ]
    await update.message.reply_text(
        "🔔 ជ្រើសពេលរំលឹក:",
        reply_markup=ReplyKeyboardMarkup(kb, one_time_keyboard=True, resize_keyboard=True)
    )
    return REMINDER_TIME

async def reminder_set_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid  = update.effective_user.id
    text = update.message.text
    if "បិទ" in text:
        set_reminder(uid, False)
        await update.message.reply_text("✅ ការរំលឹកបានបិទ!")
        return ConversationHandler.END
    time_map = {"8:00": "08:00", "12:00": "12:00", "18:00": "18:00", "20:00": "20:00"}
    for k, v in time_map.items():
        if k in text:
            set_reminder(uid, True, v)
            await update.message.reply_text(t(uid, 'reminder_set', time=v))
            break
    return ConversationHandler.END

async def delete_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(t(uid, 'delete_id'))
    return DELETE_ID

async def delete_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    try:
        eid = int(update.message.text.replace("#", "").strip())
        delete_expense(eid, uid)
        await update.message.reply_text(t(uid, 'deleted').format(eid))
    except:
        await update.message.reply_text("❌ ID មិនត្រឹមត្រូវ!")
    return ConversationHandler.END

async def ai_advice(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    logger.info(f"DEBUG: /ai called by {uid}")

    if not is_authenticated(uid):
        await update.message.reply_text(t(uid, 'pin_enter'))
        return ConversationHandler.END

    if not GEMINI_KEY:
        await update.message.reply_text(
            "❌ GEMINI_KEY មិនទាន់ set!\n"
            "សូម បន្ថែម GEMINI_KEY=AIza... ក្នុង .env file"
        )
        return ConversationHandler.END

    await update.message.reply_text(t(uid, 'ai_thinking'))

    rows   = get_monthly(uid)
    total  = get_monthly_total(uid)
    budget = get_budget(uid)

    if not rows:
        await update.message.reply_text(
            "📭 គ្មានទិន្នន័យចំណាយខែនេះ!\n"
            "សូម /add បន្ថែមចំណាយជាមុនសិន 😊"
        )
        return ConversationHandler.END

    summary = "ចំណាយខែនេះ:\n"
    for cat, amt in rows:
        summary += f"- {cat}: {amt:,.0f} រៀល\n"
    summary += f"សរុប: {total:,.0f} រៀល\nថវិកា: {budget:,.0f} រៀល"

    try:
        client = google_genai.Client(api_key=GEMINI_KEY)
        prompt = (
            "អ្នកជាទីប្រឹក្សាហិរញ្ញវត្ថុ។ "
            "វិភាគចំណាយ និងណែនាំការសន្សំប្រាក់ជាភាសាខ្មែរ "
            "(ខ្លី 200 ពាក្យ):\n\n" + summary
        )
        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=prompt
        )
        advice = response.text
        await update.message.reply_text(f"🤖 AI ណែនាំ:\n\n{advice}")

    except Exception as e:
        logger.error(f"Gemini Error [{type(e).__name__}]: {e}")
        await update.message.reply_text(
            f"❌ Gemini Error [{type(e).__name__}]:\n{str(e)[:200]}"
        )
    return ConversationHandler.END

async def receipt_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if update.message.photo:
        photo = update.message.photo[-1]
        os.makedirs("receipts", exist_ok=True)
        file  = await photo.get_file()
        path  = f"receipts/{uid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        await file.download_to_drive(path)
        await update.message.reply_text(t(uid, 'receipt_saved'))

async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    ctx.user_data.clear()
    await update.message.reply_text(t(uid, 'cancel'))
    return ConversationHandler.END

async def send_reminders(ctx: ContextTypes.DEFAULT_TYPE):
    import sqlite3
    conn = sqlite3.connect("expenses.db")
    c    = conn.cursor()
    hour = datetime.now().strftime("%H")
    c.execute("SELECT user_id FROM users WHERE daily_reminder=1 AND reminder_time LIKE ?", (f"{hour}:%",))
    rows = c.fetchall()
    conn.close()
    for (uid,) in rows:
        try:
            await ctx.bot.send_message(uid, t(uid, 'reminder_msg'))
        except Exception as e:
            logger.error(f"Reminder error for {uid}: {e}")

if __name__ == "__main__":

    if not TOKEN:
        print("❌ ERROR: TOKEN មិនទាន់ set ក្នុង .env!")
        print("   .env ត្រូវមាន: TOKEN=your_bot_token")
        exit(1)

    if not GEMINI_KEY:
        print("⚠️  WARNING: GEMINI_KEY មិនទាន់ set ក្នុង .env!")
        print("   /ai នឹងមិនដំណើរការទេ")
    else:
        print("✅ Gemini API Key: OK")

    # Start health check server for UptimeRobot
    threading.Thread(target=run_health_server, daemon=True).start()
    print(f"✅ Health server running on port {os.environ.get('PORT', 8080)}")

    init_db()
    app = ApplicationBuilder().token(TOKEN).build()

    start_conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={PIN_VERIFY: [MessageHandler(filters.TEXT & ~filters.COMMAND, pin_verify)]},
        fallbacks=common_fallbacks(),
        allow_reentry=True,
    )
    pin_conv = ConversationHandler(
        entry_points=[CommandHandler("setpin", setpin_start)],
        states={PIN_SET: [MessageHandler(filters.TEXT & ~filters.COMMAND, pin_set_handler)]},
        fallbacks=common_fallbacks(),
        allow_reentry=True,
    )
    lang_conv = ConversationHandler(
        entry_points=[CommandHandler("lang", lang_start)],
        states={LANG_CHOOSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, lang_choose)]},
        fallbacks=common_fallbacks(),
        allow_reentry=True,
    )
    add_conv = ConversationHandler(
        entry_points=[CommandHandler("add", add_start)],
        states={
            PIN_VERIFY:    [MessageHandler(filters.TEXT & ~filters.COMMAND, pin_verify)],
            CHOOSE_CAT:    [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_category)],
            ENTER_AMOUNT:  [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_amount)],
            ENTER_NOTE:    [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_note)],
            ENTER_TAG:     [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_tag)],
            IS_RECURRING:  [MessageHandler(filters.TEXT & ~filters.COMMAND, is_recurring)],
            RECURRING_INT: [MessageHandler(filters.TEXT & ~filters.COMMAND, recurring_interval)],
        },
        fallbacks=common_fallbacks(),
        allow_reentry=True,
    )
    goal_conv = ConversationHandler(
        entry_points=[CommandHandler("goal", goal_start)],
        states={
            GOAL_NAME:         [MessageHandler(filters.TEXT & ~filters.COMMAND, goal_handler)],
            GOAL_TARGET:       [MessageHandler(filters.TEXT & ~filters.COMMAND, goal_name)],
            GOAL_DEADLINE:     [MessageHandler(filters.TEXT & ~filters.COMMAND, goal_target)],
            GOAL_DEADLINE + 1: [MessageHandler(filters.TEXT & ~filters.COMMAND, goal_deadline)],
        },
        fallbacks=common_fallbacks(),
        allow_reentry=True,
    )
    budget_conv = ConversationHandler(
        entry_points=[CommandHandler("budget", budget_start)],
        states={BUDGET_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, budget_set)]},
        fallbacks=common_fallbacks(),
        allow_reentry=True,
    )
    reminder_conv = ConversationHandler(
        entry_points=[CommandHandler("reminder", reminder_start)],
        states={REMINDER_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, reminder_set_handler)]},
        fallbacks=common_fallbacks(),
        allow_reentry=True,
    )
    date_conv = ConversationHandler(
        entry_points=[CommandHandler("date", date_start)],
        states={SEARCH_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, date_search)]},
        fallbacks=common_fallbacks(),
        allow_reentry=True,
    )
    tag_conv = ConversationHandler(
        entry_points=[CommandHandler("tags", tags_start)],
        states={SEARCH_TAG: [MessageHandler(filters.TEXT & ~filters.COMMAND, tag_search)]},
        fallbacks=common_fallbacks(),
        allow_reentry=True,
    )
    delete_conv = ConversationHandler(
        entry_points=[CommandHandler("delete", delete_start)],
        states={DELETE_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_handler)]},
        fallbacks=common_fallbacks(),
        allow_reentry=True,
    )

    app.add_handler(start_conv)
    app.add_handler(pin_conv)
    app.add_handler(lang_conv)
    app.add_handler(add_conv)
    app.add_handler(goal_conv)
    app.add_handler(budget_conv)
    app.add_handler(reminder_conv)
    app.add_handler(date_conv)
    app.add_handler(tag_conv)
    app.add_handler(delete_conv)
    app.add_handler(CommandHandler("today",     today))
    app.add_handler(CommandHandler("month",     month))
    app.add_handler(CommandHandler("compare",   compare))
    app.add_handler(CommandHandler("recurring", recurring))
    app.add_handler(CommandHandler("ai",        ai_advice))
    app.add_handler(MessageHandler(filters.PHOTO, receipt_handler))

    if app.job_queue:
        app.job_queue.run_repeating(send_reminders, interval=3600, first=10)
        print("✅ Job Queue: ON")
    else:
        print("⚠️  Job Queue: OFF — run: pip install 'python-telegram-bot[job-queue]'")

    print("🤖 Bot កំពុងដំណើរការ...")
    app.run_polling()
