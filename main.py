import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from pdfminer.high_level import extract_text
from reverso_api.context import ReversoContextAPI

# إعدادات البوت
TOKEN = "6334414905:AAGdBEBDfiY7W9Nhyml1wHxSelo8gfpENR8"  
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# دالة لمعالجة أمر /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text('مرحبًا! أرسل لي ملف PDF لترجمته من الإنجليزية إلى العربية.')

# دالة لترجمة النص باستخدام Reverso
def translate_text(text):
    api = ReversoContextAPI(source_text=text, source_lang="en", target_lang="ar")
    translations = list(api.get_translations())  # تحويل الـ generator إلى قائمة
    if translations:
        return translations[0]['translation']
    return ""

# دالة لمعالجة ملفات PDF
def handle_pdf(update: Update, context: CallbackContext):
    try:
        # تحقق من وجود ملف مرفق
        if not update.message or not update.message.document:
            update.message.reply_text("يرجى إرسال ملف PDF لترجمته.")
            return

        # تحقق من أن الملف هو PDF
        if not update.message.document.mime_type == "application/pdf":
            update.message.reply_text("المرجو إرسال ملف PDF فقط.")
            return

        # تنزيل الملف
        file = update.message.document.get_file()
        file.download('input.pdf')

        # استخراج النص من PDF
        text = extract_text('input.pdf')

        # تقسيم النص إلى أجزاء (لتجنب حدود الترجمة)
        chunks = [text[i:i+500] for i in range(0, len(text), 500)]

        # ترجمة كل جزء باستخدام Reverso
        translated_text = []
        for chunk in chunks:
            translated_chunk = translate_text(chunk)
            if translated_chunk:
                translated_text.append(translated_chunk)

        # حفظ النص المترجم
        with open('translated.txt', 'w', encoding='utf-8') as f:
            f.write(' '.join(translated_text))

        # إرسال النتيجة
        update.message.reply_document(document=open('translated.txt', 'rb'))

    except Exception as e:
        update.message.reply_text(f"حدث خطأ أثناء معالجة الملف: {str(e)}")

# دالة رئيسية لتشغيل البوت
def main():
    # إنشاء Updater وإضافة Handlers
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # إضافة Handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document.mime_type("application/pdf"), handle_pdf))

    # بدء البوت
    updater.start_polling()
    updater.idle()

# تشغيل البوت
if __name__ == '__main__':
    main()
