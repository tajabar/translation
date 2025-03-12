import os
import requests
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    filters,  # تم تغيير الاسم هنا من Filters إلى filters
    CallbackContext,
)
from pypdf2 import PdfReader

# إعدادات API
APYHUB_API_KEY = "APY0ShNmihUEqMaIuecO9MOQJ9oWaBmCcLPfDzknG0URVRiDhAjU2HLznsHVkA4tX"
APYHUB_TRANSLATE_URL = "https://api.apyhub.com/translate/text"

# دالة لترجمة النص
def translate_text(text: str, target_lang: str = "ar") -> str:
    headers = {"apy-token": APYHUB_API_KEY, "Content-Type": "application/json"}
    data = {"text": text, "target": target_lang}
    response = requests.post(APYHUB_TRANSLATE_URL, json=data, headers=headers)
    return response.json().get("data", {}).get("translated")

# دالة لمعالجة ملف PDF
def process_pdf(file_path: str) -> str:
    text = ""
    with open(file_path, "rb") as f:
        reader = PdfReader(f)
        for page in reader.pages:
            text += page.extract_text()
    return text

# معالجة الأوامر
def start(update: Update, context: CallbackContext):
    update.message.reply_text("مرحبًا! أرسل لي ملف PDF باللغة الإنجليزية وسأقوم بترجمته إلى العربية.")

def handle_document(update: Update, context: CallbackContext):
    document = update.message.document
    if document.mime_type != "application/pdf":
        update.message.reply_text("❌ الرجاء إرسال ملف PDF فقط.")
        return

    file = context.bot.get_file(document.file_id)
    file_path = f"temp_{document.file_name}"
    file.download(file_path)
    
    try:
        extracted_text = process_pdf(file_path)
        translated_text = translate_text(extracted_text)
        update.message.reply_text(f"الترجمة:\n\n{translated_text}")
    except Exception as e:
        update.message.reply_text(f"❌ حدث خطأ: {str(e)}")
    finally:
        os.remove(file_path)

def main():
    TELEGRAM_TOKEN = "6334414905:AAGdBEBDfiY7W9Nhyml1wHxSelo8gfpENR8"  # التوكن الخاص بك
    updater = Updater(TELEGRAM_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(filters.Document.ALL, handle_document))  # التعديل هنا
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
