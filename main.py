import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from deep_translator import GoogleTranslator
import fitz  # PyMuPDF

# إعدادات البوت
TOKEN = "6334414905:AAGdBEBDfiY7W9Nhyml1wHxSelo8gfpENR8"  # استبدل هذا بالتوكن الخاص بك
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# دالة لمعالجة أمر /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text('مرحبًا! أرسل لي ملف PDF لترجمته من الإنجليزية إلى العربية.')

# دالة لترجمة النص باستخدام deep-translator
def translate_text(text):
    translator = GoogleTranslator(source='en', target='ar')
    translated = translator.translate(text)
    return translated

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

        # فتح ملف PDF الأصلي
        pdf_document = fitz.open('input.pdf')

        # إنشاء ملف PDF جديد
        output_pdf = fitz.open()

        # ترجمة النص في كل صفحة
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text_instances = page.get_text("dict")  # استخراج النص كـ dictionary

            # إنشاء صفحة جديدة في ملف PDF الجديد
            new_page = output_pdf.new_page(width=page.rect.width, height=page.rect.height)

            # إضافة النص المترجم إلى الصفحة الجديدة
            for block in text_instances["blocks"]:
                for line in block["lines"]:
                    for span in line["spans"]:
                        original_text = span["text"]
                        translated_text = translate_text(original_text)
                        new_page.insert_text(
                            point=(span["origin"][0], span["origin"][1]),  # نفس موقع النص الأصلي
                            text=translated_text,
                            fontsize=span["size"],
                            fontname=span["font"],
                            color=span["color"],
                        )

        # حفظ ملف PDF الجديد
        output_pdf.save('translated.pdf')
        output_pdf.close()

        # إرسال النتيجة
        update.message.reply_document(document=open('translated.pdf', 'rb'))

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
