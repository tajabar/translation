import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import PyPDF2
from reverso_api import Reverso  # تأكد من تثبيت المكتبة والتوثيق الخاص بها

# إعداد تسجيل الأخطاء
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def translate_text(text, src_lang="en", target_lang="ar"):
    # إنشاء كائن الترجمة من مكتبة reverso-api
    translator = Reverso(source=src_lang, target=target_lang)
    translated = translator.translate(text)
    return translated

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("مرحباً! أرسل لي ملف PDF لترجمته من الإنجليزية إلى العربية.")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # تحميل ملف PDF المرسل
    document = update.message.document
    file = await document.get_file()
    file_path = "document.pdf"
    await file.download_to_drive(file_path)
    
    # استخراج النص من ملف PDF
    pdf_text = ""
    with open(file_path, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                pdf_text += page_text

    if not pdf_text:
        await update.message.reply_text("لم يتمكن البوت من استخراج نص من الملف. تأكد من أن الملف يحتوي على نص قابل للنسخ.")
        return

    # ترجمة النص باستخدام reverso-api
    try:
        translated_text = translate_text(pdf_text)
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ أثناء الترجمة: {e}")
        return

    # إرسال النص المترجم للمستخدم (قد تحتاج لتقسيم النص إذا كان طويلاً جداً)
    await update.message.reply_text("هذا هو النص المترجم:\n" + translated_text)

if __name__ == '__main__':
    # استبدل "YOUR_TELEGRAM_BOT_TOKEN" بالتوكن الخاص ببوت تلغرام الخاص بك
    app = ApplicationBuilder().token("YOUR_TELEGRAM_BOT_TOKEN").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_document))

    app.run_polling()
