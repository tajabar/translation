import requests
import os
from telegram import Update, Bot, Document
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# ضع هنا التوكن الخاص بتيليجرام
TELEGRAM_BOT_TOKEN = "5146976580:AAE2yXc-JK6MIHVlLDy-O4YODucS_u7Zq-8"
MONICA_API_KEY = "sk-bD-nYh2aYbDc3YN07uJupM7FNlBRk6zfx_qSsGfAyJ5sE3GZnx1hk5sJjBtbHqK26Hm0ig77XabG3KnEnf_EPoQtSNG8"
MONICA_API_URL = "https://api.monica.im/translate/pdf"

# دالة لبدء البوت
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("أهلاً! أرسل لي ملف PDF وسأقوم بترجمته لك من العربية إلى الإنجليزية.")

# دالة لمعالجة ملفات PDF
def handle_document(update: Update, context: CallbackContext) -> None:
    document = update.message.document
    file = context.bot.get_file(document.file_id)
    file_path = f"downloaded_{document.file_name}"
    
    file.download(file_path)
    translated_file_path = translate_pdf(file_path)
    
    if translated_file_path:
        update.message.reply_document(document=open(translated_file_path, "rb"))
        os.remove(translated_file_path)
    os.remove(file_path)

# دالة لترجمة الملف عبر API
def translate_pdf(file_path: str) -> str:
    files = {"file": open(file_path, "rb")}
    headers = {"Authorization": f"Bearer {MONICA_API_KEY}"}
    data = {"source_lang": "ar", "target_lang": "en"}
    
    response = requests.post(MONICA_API_URL, files=files, headers=headers, data=data)
    
    if response.status_code == 200:
        translated_pdf_url = response.json().get("translated_pdf_url")
        translated_file_path = "translated.pdf"
        
        with open(translated_file_path, "wb") as f:
            f.write(requests.get(translated_pdf_url).content)
        
        return translated_file_path
    else:
        return None

# إعداد البوت
def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document.mime_type("application/pdf"), handle_document))
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
