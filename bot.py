from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackContext
from dotenv import load_dotenv
import random
import os
import logging
from datetime import time, datetime

from web_scraping import Scrape
from data_models import Model

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
    ]

async def set_daily_time(update: Update, context: CallbackContext):
    telegramId = update.effective_user.id
    try:
        args = context.args
        if len(args) != 2:
            await update.message.reply_text("Lütfen saati ve dakikayı şu formatta giriniz: /set 9 0")
            return

        hour = int(args[0])
        minute = int(args[1])

        if not (0 <= hour < 24) or not (0 <= minute < 60):
            await update.message.reply_text("Geçerli bir saat ve dakika girin! Örn: /set 9 0")
            return
        telegramId = update.effective_user.id
        kayitli_kullanicilar = model.check_all()
        sub_ids = [user[0] for user in kayitli_kullanicilar]

        print(sub_ids)
        print(telegramId)

        for id in sub_ids:
            if int(id) == int(telegramId):
                callback_send_sign_comment(context, hour - 3, minute, telegramId)
                await update.message.reply_text(f"Burç yorumları her gün {hour:02}:{minute:02} saatine ayarlandı!")
                return
        await update.message.reply_text("Önce bir burç aboneliği oluşturun! Örn: /abonelik kova")
    except ValueError:
        await update.message.reply_text("Geçerli bir saat ve dakika girin! Örn: /set 9 0")

def restart(context: CallbackContext):
    logger.info("Bot is restarting...")
    try:
        model.clear_zodiac_signs()
        model.clear_tarot_cards()
        logger.info("Database is cleared.")
        
        scrape.sign_content_push()
        scrape.tarot_content_push() 
        model.remove_duplicates_if_exists()
        logger.info("Database is updated.")
    except Exception as e:
        logger.error(f"An error occurred while restarting the bot: {e}")

# Define command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is ready. Use /tarot or /burc <sign> commands.")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "Günlük burç yorumları ve tarot falı hakkında bilgi almak için aşağıdaki komutları kullanabilirsiniz:\n\n"
        "/tarot: Rastgele bir tarot kartı çeker.\n\n"
        "/burc <burç>: Belirtilen burcun günlük yorumunu gösterir. (Örnek: /burc kova)"
        "/abonelik <burç>: Günlük burç yorumlarını almak için abone olun. (Örnek: /abonelik kova)"
        "/abonelikiptal: Aboneliği iptal eder."
        "/set <saat> <dakika>: Günlük burç yorumlarının gönderileceği saati ayarlar. (Örnek: /set 9 0)"
    )
    await update.message.reply_text(text)

async def abonelik(update: Update, context: ContextTypes.DEFAULT_TYPE):    
    user = update.message.from_user
    first_name = user["first_name"]
    last_name = user["last_name"]
    telegram_id = user["id"]
    check_id = model.check_person(telegram_id)
    zodiac_sign = None
    
    try:
        if check_id is None:
            if not context.args:
                await update.message.reply_text(
                    "Lütfen burcunuzu girin. (Örnek: /abonelik kova)\n\n Burçlar:\n balik, kova, oglak, yay, akrep, terazi, basak, aslan, yengec, ikizler, boga, koc"
                )
                return
            
            zodiac_sign = context.args[0].lower()
            if zodiac_sign not in horoscope_signs:
                await update.message.reply_text(
                    "Geçerli bir burç girin. (Örnek: /abonelik kova)\n\n Burçlar:\n balik, kova, oglak, yay, akrep, terazi, basak, aslan, yengec, ikizler, boga, koc"
                )
                return
            
            model.add_user(telegram_id, first_name, last_name, zodiac_sign)
            await update.message.reply_text(
                f"Abonelik kaydınız oluşturuldu! Günlük burç yorumlarınız {zodiac_sign} burcu için paylaşılacaktır."
            )
            return
        else:
            await update.message.reply_text("Zaten bir aboneliğiniz var.")
            return
    except Exception as e:
        logger.error(f"An error occurred while checking the subscription: {e}")
        await update.message.reply_text("Bir hata oluştu, lütfen daha sonra tekrar deneyin.")
        return

async def abonelikiptal(update:Update, context:ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    telegramId= user["id"]
    check_id = model.check_person(telegramId)
    if check_id is None:
        text = "Aboneliğiniz bulunmamaktadır."
        await update.message.reply_text(text)
    else:
        model.delete_person(telegramId)
        text = "Aboneliğiniz iptal edilmiştir."
        await update.message.reply_text(text)
    info = update.message
    messages_to_add(info)
    logger.info(f"/abonelikiptal komutu tamamlandı. Kullanıcı: {user.first_name} ({user.id})")


async def tarot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info = update.message
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
            messages_to_add(info)
        else:
            await update.message.reply_text(embed)
            messages_to_add(info)
    except Exception as e:
        logger.error(f"An error occurred while getting a tarot card: {e}")
        await update.message.reply_text("Bir hata oluştu, lütfen daha sonra tekrar deneyin.")

async def burc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info = update.message
    if len(context.args) == 0:
        await update.message.reply_text(
            "Lütfen bir burç ismi girin. (Türkçe karakter kullanmayınız.)\n\n"
            "Burçlar: balik, kova, oglak, yay, akrep, terazi, basak, aslan, yengec, ikizler, boga, koc"
        )
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
                    messages_to_add(info)
                else:
                    await update.message.reply_text(embed)
                    messages_to_add(info)
                break
    else:
        await update.message.reply_text(
            "Geçerli bir burç ismi giriniz. (Türkçe karakter kullanmayınız.)\n\n"
            "Burçlar: balik, kova, oglak, yay, akrep, terazi, basak, aslan, yengec, ikizler, boga, koc"
        )

async def send_sign_comment(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    telegramId = job.data.get("telegramId", "Unknown")  # Kullanıcı ID'si context'ten alınır
    logger.info(f"Running job for user {telegramId}")

    kayitli_kullanicilar = model.check_all()
    signs = model.get_zodiac_signs()

    try:
        user_data = next((user for user in kayitli_kullanicilar if user[0] == telegramId), None)
        if not user_data:
            logger.info(f"User {telegramId} not found in database.")
            return

        user_sign = user_data[3]
        for sign in signs:
            if sign.name == user_sign:
                embed = f"Ayın {sign.date}. günü için {sign.name} burcu günlük yorumu:\n\n{sign.description}\n\n"
                if sign.image:
                    await context.bot.send_photo(chat_id=telegramId, photo=sign.image, caption=embed)
                else:
                    await context.bot.send_message(chat_id=telegramId, text=embed)
    except Exception as e:
        logger.error(f"An error occurred while sending zodiac sign comments for user {telegramId}: {e}")

def messages_to_add(info):
    user = info.from_user
    first_name = user["first_name"]
    last_name = user["last_name"]
    telegramId = user["id"]
    message = info.text
    model.add_message(telegramId, first_name, last_name, message)

def callback_restart(context: ContextTypes.DEFAULT_TYPE):
    timer = time(hour=20, minute=59, second=0)
    context.job_queue.run_daily(restart, timer, days=(0, 1, 2, 3, 4, 5, 6))

def callback_send_sign_comment(context: CallbackContext, hour: int, minute: int, telegramId: int):
    job_name = f"daily_sign_comment_{telegramId}"
    existing_jobs = context.job_queue.get_jobs_by_name(job_name)
    for job in existing_jobs:
        job.schedule_removal()

    timer = time(hour=hour, minute=minute, second=0)
    context.job_queue.run_daily(
        send_sign_comment,
        timer,
        days=(0, 1, 2, 3, 4, 5, 6),
        name=job_name,
        data={"telegramId": telegramId}
    )
    logger.info(f"Job scheduled: {job_name} for user {telegramId} at {hour + 3:02}:{minute:02}")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("tarot", tarot))
    application.add_handler(CommandHandler("burc", burc))
    application.add_handler(CommandHandler("abonelik", abonelik))
    application.add_handler(CommandHandler("abonelikiptal", abonelikiptal))
    application.add_handler(CommandHandler("set", set_daily_time))  # Yeni komut eklendi

    restart(application)
    callback_restart(application)
    application.run_polling()


if __name__ == "__main__":
    main()
