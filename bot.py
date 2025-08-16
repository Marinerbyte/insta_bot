import os
import requests
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, Filters, Updater

SUPABASE_URL = os.getenv("SUPABASE_PROJECT_URL")  # e.g. https://xyz.supabase.co
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # service_role key

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

def is_master(user_id):
    url = f"{SUPABASE_URL}/rest/v1/masters?telegram_user_id=eq.{user_id}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200 and r.json():
        return True
    return False

def add_master(user_id, name):
    url = f"{SUPABASE_URL}/rest/v1/masters"
    payload = {
        "telegram_user_id": user_id,
        "name": name
    }
    r = requests.post(url, headers=HEADERS, json=payload)
    return r.status_code == 201

def remove_master(user_id):
    url = f"{SUPABASE_URL}/rest/v1/masters?telegram_user_id=eq.{user_id}"
    r = requests.delete(url, headers=HEADERS)
    return r.status_code == 204

def ban_user(user_id):
    url = f"{SUPABASE_URL}/rest/v1/banned_users"
    payload = {
        "telegram_user_id": user_id
    }
    r = requests.post(url, headers=HEADERS, json=payload)
    return r.status_code == 201

def unban_user(user_id):
    url = f"{SUPABASE_URL}/rest/v1/banned_users?telegram_user_id=eq.{user_id}"
    r = requests.delete(url, headers=HEADERS)
    return r.status_code == 204

def is_banned(user_id):
    url = f"{SUPABASE_URL}/rest/v1/banned_users?telegram_user_id=eq.{user_id}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200 and r.json():
        return True
    return False

def increment_download_count(user_id, url):
    api_url = f"{SUPABASE_URL}/rest/v1/downloads"
    payload = {"telegram_user_id": user_id, "url": url}
    requests.post(api_url, headers=HEADERS, json=payload)

def get_status():
    masters_count = requests.get(f"{SUPABASE_URL}/rest/v1/masters?select=id", headers=HEADERS).json()
    banned_count = requests.get(f"{SUPABASE_URL}/rest/v1/banned_users?select=id", headers=HEADERS).json()
    downloads_count = requests.get(f"{SUPABASE_URL}/rest/v1/downloads?select=id", headers=HEADERS).json()
    return f"Masters: {len(masters_count)}\nBanned Users: {len(banned_count)}\nTotal Downloads: {len(downloads_count)}"

# Telegram command handlers
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome! Send Instagram video link to download.\nAdmins can use commands starting with /")

def masteradd(update: Update, context: CallbackContext):
    user = update.message.from_user
    if not is_master(user.id):
        update.message.reply_text("You are not authorized.")
        return
    if len(context.args) != 2:
        update.message.reply_text("Usage: /masteradd <user_id> <name>")
        return
    new_user_id = int(context.args[0])
    new_user_name = context.args[11]
    if add_master(new_user_id, new_user_name):
        update.message.reply_text(f"Added master: {new_user_id} - {new_user_name}")
    else:
        update.message.reply_text("Failed to add master.")

def masterdel(update: Update, context: CallbackContext):
    user = update.message.from_user
    if not is_master(user.id):
        update.message.reply_text("You are not authorized.")
        return
    if len(context.args) != 1:
        update.message.reply_text("Usage: /masterdel <user_id>")
        return
    del_user_id = int(context.args[0])
    if remove_master(del_user_id):
        update.message.reply_text(f"Removed master: {del_user_id}")
    else:
        update.message.reply_text("Failed to remove master.")

def ban(update: Update, context: CallbackContext):
    user = update.message.from_user
    if not is_master(user.id):
        update.message.reply_text("You are not authorized.")
        return
    if len(context.args) != 1:
        update.message.reply_text("Usage: /ban <user_id>")
        return
    ban_user_id = int(context.args[0])
    if ban_user(ban_user_id):
        update.message.reply_text(f"Banned user: {ban_user_id}")
    else:
        update.message.reply_text("Failed to ban user.")

def unban(update: Update, context: CallbackContext):
    user = update.message.from_user
    if not is_master(user.id):
        update.message.reply_text("You are not authorized.")
        return
    if len(context.args) != 1:
        update.message.reply_text("Usage: /unban <user_id>")
        return
    unban_user_id = int(context.args[0])
    if unban_user(unban_user_id):
        update.message.reply_text(f"Unbanned user: {unban_user_id}")
    else:
        update.message.reply_text("Failed to unban user.")

def status(update: Update, context: CallbackContext):
    user = update.message.from_user
    if not is_master(user.id):
        update.message.reply_text("You are not authorized.")
        return
    s = get_status()
    update.message.reply_text(s)

def message_handler(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    text = update.message.text
    if is_banned(user_id):
        update.message.reply_text("You are banned from using this bot.")
        return
    if "instagram.com" in text:
        update.message.reply_text("Downloading video... Please wait.")
        # Your download logic here (call to actual video download function)
        # After download success:
        increment_download_count(user_id, text)
        update.message.reply_text("Video downloaded and logged!")
    else:
        update.message.reply_text("Send a valid Instagram video link.")

def main():
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("masteradd", masteradd))
    dp.add_handler(CommandHandler("masterdel", masterdel))
    dp.add_handler(CommandHandler("ban", ban))
    dp.add_handler(CommandHandler("unban", unban))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
    
