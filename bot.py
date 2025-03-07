from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler
import logging
import requests

# ✅ LOGGING SETUP
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# ✅ CHANNEL & BOT SETTINGS
CHANNEL_USERNAME = "@referearn01g"
ADMIN_ID = 123456789  # अपना टेलीग्राम यूज़र ID डालें
users_data = {}

# ✅ FUNCTION: Check if user has joined the channel
def is_user_subscribed(user_id, bot_token):
    url = f"https://api.telegram.org/bot{bot_token}/getChatMember?chat_id={CHANNEL_USERNAME}&user_id={user_id}"
    response = requests.get(url).json()
    status = response.get("result", {}).get("status", "")
    return status in ["member", "administrator", "creator"]

# ✅ FUNCTION: Start Command
def start(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    bot_token = context.bot.token

    # ✅ Check if user is subscribed
    if not is_user_subscribed(user_id, bot_token):
        keyboard = [
            [InlineKeyboardButton("🔔 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}")],
            [InlineKeyboardButton("✅ I have joined", callback_data="check_subscription")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("🚨 Please join our channel first!\n👇 Click the button below:", reply_markup=reply_markup)
        return

    # ✅ Generate referral link **(BUG FIXED - सही जगह पर डाला)**
    referral_link = f"https://t.me/YOUR_BOT_USERNAME?start={user_id}"
    
    users_data.setdefault(user_id, {"balance": 0, "referrals": 0})
    
    keyboard = [
        [InlineKeyboardButton("🔍 Check Balance", callback_data="balance")],
        [InlineKeyboardButton("💰 Referral Link", callback_data="referral")],
        [InlineKeyboardButton("🎁 Daily Bonus", callback_data="daily_bonus")],
        [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard")],
        [InlineKeyboardButton("🏧 Withdraw", callback_data="withdraw")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        f"🙏 Welcome {update.message.chat.first_name}!\n\n"
        f"Invite friends & earn ₹5 per referral.\n\n"
        f"🎯 Your referral link:\n{referral_link}",
        reply_markup=reply_markup
    )

# ✅ FUNCTION: Button Handler
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.message.chat_id

    if user_id not in users_data:
        users_data[user_id] = {"balance": 0, "referrals": 0}

    if query.data == "balance":
        balance = users_data[user_id]["balance"]
        query.answer()
        query.edit_message_text(f"💰 Your Balance: ₹{balance}")

    elif query.data == "referral":
        referral_link = f"https://t.me/YOUR_BOT_USERNAME?start={user_id}"
        query.answer()
        query.edit_message_text(f"🔗 Your Referral Link:\n{referral_link}")

    elif query.data == "daily_bonus":
        users_data[user_id]["balance"] += 2  # 🎁 ₹2 Bonus
        query.answer()
        query.edit_message_text(f"🎉 You received ₹2 daily bonus!\n💰 New Balance: ₹{users_data[user_id]['balance']}")

    elif query.data == "withdraw":
        if users_data[user_id]["balance"] >= 50:
            context.bot.send_message(ADMIN_ID, f"💰 Withdrawal Request!\nUser: {user_id}\nAmount: ₹50")
            users_data[user_id]["balance"] -= 50
            query.answer()
            query.edit_message_text("✅ Withdrawal request sent! Admin will review soon.")
        else:
            query.answer()
            query.edit_message_text("❌ Minimum ₹50 required for withdrawal!")

    elif query.data == "leaderboard":
        top_users = sorted(users_data.items(), key=lambda x: x[1]["referrals"], reverse=True)[:10]
        leaderboard_text = "🏆 *Top 10 Referrers:*\n\n" + "\n".join([f"{i+1}. User {u[0]} - {u[1]['referrals']} Referrals" for i, u in enumerate(top_users)])
        query.answer()
        query.edit_message_text(leaderboard_text, parse_mode="Markdown")

# ✅ FUNCTION: Handle New Users from Referrals
def handle_new_user(update: Update, context: CallbackContext):
    args = context.args
    new_user_id = update.message.chat_id

    if args:
        referrer_id = int(args[0])
        if referrer_id != new_user_id and referrer_id in users_data:
            users_data[referrer_id]["balance"] += 5  # ✅ ₹5 Referral Bonus
            users_data[referrer_id]["referrals"] += 1
            update.message.reply_text("🎉 You joined using a referral link!")
            context.bot.send_message(referrer_id, f"🎊 New Referral! You earned ₹5.\n💰 New Balance: ₹{users_data[referrer_id]['balance']}")

# ✅ MAIN FUNCTION
def main():
    TOKEN = "8029651365:AAHsOFctfxcNuCk85_ph1sJf61uwO_kr504"
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("leaderboard", button_handler))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_new_user))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
