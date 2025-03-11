import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from pdfminer.high_level import extract_text
from reverso_api.context import ReversoContextAPI

# إعدادات البوت
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def start(update: Update, context: CallbackContext):
    update.message.reply_text('مرحبًا! أرسل لي ملف PDF لترجمته من الإنجليزية إلى العربية.')

def handle_pdf(update: Update, context: CallbackContext):
    # تنزيل الملف
    file = update.message.document.get_file()
    file.download('input.pdf')
    
    # استخراج النص من PDF
    text = extract_text('input.pdf')
    
    # تقسيم النص إلى أجزاء (لتجنب حدود الترجمة)
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    
    # ترجمة كل جزء باستخدام Reverso
    translated_text = []
    api = ReversoContextAPI(source_text="", source_lang="en", target_lang="ar")
    for chunk in chunks:
        translations = api.get_translations(chunk)
        if translations:
            translated_text.append(translations[0]['translation'])
    
    # حفظ النص المترجم
    with open('translated.txt', 'w', encoding='utf-8') as f:
        f.write(' '.join(translated_text))
    
    # إرسال النتيجة
    update.message.reply_document(document=open('translated.txt', 'rb'))

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document, handle_pdf))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
