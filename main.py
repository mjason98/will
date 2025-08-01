from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import logging, os
from time import time
from dotenv import load_dotenv
from will_utils import request_wills_house_ids_url, HousesStore

load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO  # Use DEBUG for more details
)
logger = logging.getLogger(__name__)

# Replace with your bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")
WILL_UPDATE = 30  # Update interval in seconds

# house data =============
HOUSES_SET = HousesStore()
# ========================

# Background task
async def periodic_task(context: ContextTypes.DEFAULT_TYPE) -> None:
    global HOUSES_SET

    new_urls = set()
    already_new = HOUSES_SET.is_new(str(context.job.chat_id)) # type: ignore
    new_urls |= already_new

    if HOUSES_SET.is_updated(WILL_UPDATE):
        logger.info(f"Requested new update")
        ids_data = request_wills_house_ids_url()
        ids = list(ids_data.keys())
        urls = [data["url"] for data in ids_data.values()]
        logger.info(f"New IDs: {ids}")
        update_set = HOUSES_SET.update(ids, urls, str(context.job.chat_id)) # type: ignore
        new_urls |= update_set
    
    is_new_update = len(new_urls) > 0
    logger.info(f"new update: {is_new_update}")

    if is_new_update:
        logger.info(f"New houses found in update")
        for url in new_urls:
            await context.bot.send_message(chat_id=context.job.chat_id,  # type: ignore
                                           text=f"New house: {url}")

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ========== JOB QUEUE SETUP ==========
    user_id = update.effective_chat.id # type: ignore
    job_name = str(user_id) + "_job"
    logger.info(f"User {user_id} started the bot.")

    await update.message.reply_text("Hi! You'll now receive periodic updates.") # type: ignore

    context.job_queue.run_repeating(periodic_task, interval=WILL_UPDATE, first=WILL_UPDATE, # type: ignore
                                    chat_id=user_id,
                                    name=job_name)
    # ====================================


if __name__ == '__main__':
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is not set. Please set it in the .env file.")
        exit(1)

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    logger.info("Bot is running...")
    app.run_polling(poll_interval=1)