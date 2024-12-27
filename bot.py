from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackContext
from dotenv import load_dotenv
from web_scraping import Scrape
from data_models import Model
import random
import os
import logging
from datetime import time, datetime

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s", 
    datefmt="%Y-%m-%d %H:%M:%S", 
    level=logging.INFO  
)

logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger("TelegramBot") 

model = Model()
scrape = Scrape()
model.create_tables()

horoscope_signs = [
    "balik", "kova", "oglak", "yay", "akrep", "terazi",
    "basak", "aslan", "yengec", "ikizler", "boga", "koc"
] # Turkish names of zodiac signs

def restart(context: CallbackContext):    
    logger.info("Bot is restarting...")
    try:
        try:
            model.clear_zodiac_signs()
            model.clear_tarot_cards()
            logging.info("Database is cleared.")
        except Exception as e:
            logger.error(f"An error occurred while clearing the database: {e}")
        try:
            scrape.sign_content_push()  # Scrape horoscope content and push to database
            scrape.tarot_content_push()  # Scrape tarot content and push to database
            model.remove_duplicates_if_exists()
            logger.info("Database is updated.")
        except Exception as e:
            logger.error(f"An error occurred while updating the database: {e}")
    except Exception as e:
        logger.error(f"An error occurred while restarting the bot: {e}")

# Define command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is ready. Use /tarot or /burc <sign> commands.")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """Günlük burç yorumları ve tarot falı hakkında bilgi almak için aşağıdaki komutları kullanabilirsiniz:\n\n
    /tarot: Rastgele bir tarot kartı çeker.\n\n/burc <burç>: Belirtilen burcun günlük yorumunu gösterir. (Örnek: /burc kova)
    """
    await update.message.reply_text()

async def tarot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        tarot_cards = model.get_tarot_cards()
        random_card = random.choice(tarot_cards)
        embed = f"{random_card.name}\n\n{random_card.description}"
        if random_card.image:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=random_card.image,         
                caption=embed                 
            )
        else:
            await update.message.reply_text(embed)

    except Exception as e:
        logger.error(f"An error occurred while getting a tarot card: {e}")
        await update.message.reply_text("Bir hata oluştu, lütfen daha sonra tekrar deneyin.")

    
async def burc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("Lütfen bir burç ismi girin. (Türkçe karakter kullanmayınız.)\n\n burçlar: balik, kova, oglak, yay, akrep, terazi, basak, aslan, yengec, ikizler, boga, koc")
        return

    arg = context.args[0].lower()
    if arg in horoscope_signs:
        signs = model.get_zodiac_signs()
        for sign in signs:
            if sign.name == arg:
                embed = f"Ayın {sign.date}. günü için {sign.name} burcu günlük yorumu:\n\n{sign.description}\n\n"
                if sign.image:
                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=sign.image,         
                        caption=embed                 
                    )
                else:
                    await update.message.reply_text(embed)
                break
    else:
        await update.message.reply_text("Geçerli bir burç ismi giriniz. (Türkçe karakter kullanmayınız.)\n\n burçlar: balik, kova, oglak, yay, akrep, terazi, basak, aslan, yengec, ikizler, boga, koc")

def callbackRestart(context: ContextTypes.DEFAULT_TYPE):
    timer = time(hour=17, minute=0, second=0)
    context.job_queue.run_daily(restart, timer, days=(0,1,2,3,4,5,6))

# Main function to start the bot
def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("tarot", tarot))
    application.add_handler(CommandHandler("burc", burc))
    restart(application)
    callbackRestart(application, )
    
    application.run_polling()

if __name__ == "__main__":
    main()

