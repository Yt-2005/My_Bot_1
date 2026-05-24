TEXTS = {
    'km': {
        'welcome': (
            "👋 សួស្តី! ខ្ញុំជា Bot កត់ត្រាចំណាយរបស់អ្នក!\n\n"
            "📌 របៀបប្រើ:\n"
            "/add — បន្ថែមចំណាយ\n"
            "/today — ចំណាយថ្ងៃនេះ\n"
            "/month — សង្ខេបខែ\n"
            "/compare — ប្រៀបធៀបខែ\n"
            "/date — ស្វែងរកតាមកាលបរិច្ឆេទ\n"
            "/tags — ស្វែងរកតាម Tag\n"
            "/recurring — ចំណាយដដែលៗ\n"
            "/goal — គោលដៅសន្សំ\n"
            "/budget — កំណត់ថវិកា\n"
            "/reminder — កំណត់ការរំលឹក\n"
            "/setpin — កំណត់ PIN\n"
            "/lang — ប្តូរភាសា\n"
            "/ai — AI ណែនាំ\n"
            "/delete — លុបការកត់ត្រា"
        ),
        'choose_cat': "💰 ជ្រើសប្រភេទចំណាយ:",
        'enter_amount': "💵 បញ្ចូលចំនួនទឹកប្រាក់:",
        'enter_note': "📝 បញ្ចូលកំណត់សម្គាល់ (ឬវាយ '-' បើគ្មាន):",
        'enter_tag': "🏷️ បញ្ចូល Tag (ឧ. ការងារ, ផ្ទះ) ឬ '-' បើគ្មាន:",
        'is_recurring': "🔄 តើជាចំណាយដដែលៗទេ?",
        'recurring_interval': "⏰ ជ្រើសពេលវេលា:",
        'saved': "✅ បានកត់ត្រា!\n📂 {cat}\n💵 {amt:,.0f}\n📝 {note}\n🏷️ {tag}",
        'no_expense': "📭 គ្មានចំណាយទេ!",
        'today_header': "📊 ចំណាយថ្ងៃនេះ:\n\n",
        'month_header': "📅 សង្ខេបខែ {month}:\n\n",
        'total': "\n💰 សរុប: {total:,.0f}",
        'invalid_amount': "❌ សូមបញ្ចូលលេខប៉ុណ្ណោះ!",
        'cancel': "❌ បោះបង់រួចហើយ!",
        'enter_pin': "🔐 បញ្ចូល PIN 4 ខ្ទង់:",
        'pin_set': "✅ PIN បានកំណត់!",
        'pin_wrong': "❌ PIN មិនត្រូវ! សាកល្បងម្តងទៀត:",
        'pin_enter': "🔐 បញ្ចូល PIN ដើម្បីចូល Bot:",
        'lang_changed': "✅ ប្តូរភាសាជា ខ្មែរ រួចហើយ!",
        'budget_set': "✅ ថវិកាខែ {budget:,.0f} បានកំណត់!",
        'budget_warning': "⚠️ អ្នកបានប្រើ {pct:.0f}% នៃថវិកា ({used:,.0f}/{budget:,.0f})!",
        'budget_exceeded': "🚨 អ្នកលើសថវិកា! ({used:,.0f}/{budget:,.0f})",
        'reminder_set': "✅ ការរំលឹកប្រចាំថ្ងៃ ម៉ោង {time} បានកំណត់!",
        'reminder_msg': "🔔 កុំភ្លេចកត់ត្រាចំណាយថ្ងៃនេះ!\nប្រើ /add ដើម្បីបន្ថែម។",
        'goal_name': "🎯 ឈ្មោះគោលដៅ (ឧ. ទិញម៉ូតូ):",
        'goal_target': "💰 ចំនួនដែលត្រូវសន្សំ (រៀល):",
        'goal_deadline': "📅 ថ្ងៃផុតកំណត់ (YYYY-MM-DD):",
        'goal_saved': "✅ គោលដៅ '{name}' ចំនួន {target:,.0f} បានកំណត់!",
        'goals_header': "🎯 គោលដៅសន្សំរបស់អ្នក:\n\n",
        'goal_progress': "• {name}: {saved:,.0f}/{target:,.0f} ({pct:.0f}%) {bar}\n  📅 {deadline}\n\n",
        'enter_date': "📅 បញ្ចូលថ្ងៃ (YYYY-MM-DD):",
        'enter_tag_search': "🏷️ បញ្ចូល Tag ដែលចង់ស្វែងរក:",
        'compare_header': "📊 ប្រៀបធៀបខែ:\n\n",
        'delete_id': "🗑️ បញ្ចូល ID ចំណាយដែលចង់លុប (ដូចបង្ហាញ #ID):",
        'deleted': "✅ បានលុបចំណាយ #{}!",
        'ai_thinking': "🤖 AI កំពុងវិភាគ...",
        'receipt_saved': "📸 រូបបង្កាន់ដៃបានរក្សាទុក!",
        'yes': "✅ បាទ/ចាស",
        'no': "❌ ទេ",
    },
    'en': {
        'welcome': (
            "👋 Hello! I'm your Expense Tracker Bot!\n\n"
            "📌 Commands:\n"
            "/add — Add expense\n"
            "/today — Today's expenses\n"
            "/month — Monthly summary\n"
            "/compare — Compare months\n"
            "/date — Search by date\n"
            "/tags — Search by tag\n"
            "/recurring — Recurring expenses\n"
            "/goal — Savings goals\n"
            "/budget — Set budget\n"
            "/reminder — Set reminder\n"
            "/setpin — Set PIN\n"
            "/lang — Change language\n"
            "/ai — AI advice\n"
            "/delete — Delete record"
        ),
        'choose_cat': "💰 Choose category:",
        'enter_amount': "💵 Enter amount:",
        'enter_note': "📝 Enter note (or '-' for none):",
        'enter_tag': "🏷️ Enter tag (e.g. work, home) or '-' for none:",
        'is_recurring': "🔄 Is this a recurring expense?",
        'recurring_interval': "⏰ Select interval:",
        'saved': "✅ Saved!\n📂 {cat}\n💵 {amt:,.0f}\n📝 {note}\n🏷️ {tag}",
        'no_expense': "📭 No expenses found!",
        'today_header': "📊 Today's Expenses:\n\n",
        'month_header': "📅 Month {month} Summary:\n\n",
        'total': "\n💰 Total: {total:,.0f}",
        'invalid_amount': "❌ Please enter numbers only!",
        'cancel': "❌ Cancelled!",
        'enter_pin': "🔐 Enter 4-digit PIN:",
        'pin_set': "✅ PIN has been set!",
        'pin_wrong': "❌ Wrong PIN! Try again:",
        'pin_enter': "🔐 Enter PIN to access Bot:",
        'lang_changed': "✅ Language changed to English!",
        'budget_set': "✅ Monthly budget {budget:,.0f} set!",
        'budget_warning': "⚠️ You've used {pct:.0f}% of budget ({used:,.0f}/{budget:,.0f})!",
        'budget_exceeded': "🚨 Over budget! ({used:,.0f}/{budget:,.0f})",
        'reminder_set': "✅ Daily reminder set at {time}!",
        'reminder_msg': "🔔 Don't forget to log your expenses today!\nUse /add to add one.",
        'goal_name': "🎯 Goal name (e.g. Buy motorbike):",
        'goal_target': "💰 Target amount:",
        'goal_deadline': "📅 Deadline (YYYY-MM-DD):",
        'goal_saved': "✅ Goal '{name}' for {target:,.0f} set!",
        'goals_header': "🎯 Your Savings Goals:\n\n",
        'goal_progress': "• {name}: {saved:,.0f}/{target:,.0f} ({pct:.0f}%) {bar}\n  📅 {deadline}\n\n",
        'enter_date': "📅 Enter date (YYYY-MM-DD):",
        'enter_tag_search': "🏷️ Enter tag to search:",
        'compare_header': "📊 Month Comparison:\n\n",
        'delete_id': "🗑️ Enter expense ID to delete (shown as #ID):",
        'deleted': "✅ Deleted expense #{}!",
        'ai_thinking': "🤖 AI is analyzing...",
        'receipt_saved': "📸 Receipt image saved!",
        'yes': "✅ Yes",
        'no': "❌ No",
    }
}

def t(user_id, key, **kwargs):
    from database import get_language
    lang = get_language(user_id)
    text = TEXTS.get(lang, TEXTS['km']).get(key, key)
    return text.format(**kwargs) if kwargs else text
