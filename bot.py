import os
import logging
from telegram import Update
from telegram.ext import CallbackContext
from telegram import Bot
from download import download_instagram_video
from filemanage import safe_delete

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MAX_MB = int(os.getenv("MAX_MB", 50))

telegram_bot = Bot(token=TELEGRAM_TOKEN)


def handle_update(update_json: dict):
    """Handle incoming Telegram update JSON (from Flask webhook)."""
    update = Update.de_json(update_json, telegram_bot)

    if update.message and update.message.text:
        url = update.message.text.strip()

        if "instagram.com" not in url:
            update.message.reply_text("⚠️ Please send a valid Instagram video link.")
            return

        chat_id = update.message.chat_id
        try:
            update.message.reply_text("⏳ Downloading video... Please wait.")

            video_path = download_instagram_video(url, MAX_MB)

            if not video_path:
                update.message.reply_text("❌ Failed to download video.")
                return

            with open(video_path, "rb") as video_file:
                telegram_bot.send_video(chat_id=chat_id, video=video_file)

            update.message.reply_text("✅ Here is your video!")
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            update.message.reply_text("❌ Something went wrong while processing the video.")
        finally:
            safe_delete(video_path if 'video_path' in locals() else None)
