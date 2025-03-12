import logging
import io
import requests
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import PyPDF2

‎# إعدادات البوت ومفتاح الترجمة
TELEGRAM_BOT_TOKEN = "6334414905:AAGdBEBDfiY7W9Nhyml1wHxSelo8gfpENR8"
YANDEX_API_KEY = "aje8gi5i95c2mra75nub"
YANDEX_TRANSLATE_URL = "https://translate.yandex.net/api/v1.5/tr.json/translate"

‎# إعداد تسجيل الأخطاء
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update, context):
    await update.message.reply_text("مرحباً! أرسل لي ملف PDF وسأقوم بترجمته.")

def translate_text(text):
    params = {
        "key": YANDEX_API_KEY,
        "text": text,
        "lang": "en-ar"
    }
    try:
        response = requests.get(YANDEX_TRANSLATE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if data.get("code") == 200:
            return " ".join(data["text"])
        else:
            return f"خطأ أثناء الترجمة: {data.get('code')}"
    except Exception as e:
        logger.error("Error during translation: %s", e)
        return "فشل الاتصال بخدمة الترجمة."

async def handle_document(update, context):
    document = update.message.document
    if document.mime_type != "application/pdf":
        await update.message.reply_text("يرجى إرسال ملف PDF فقط.")
        return

    await update.message.reply_text("يتم تحميل الملف ومعالجته...")
    file = await document.get_file()
    file_content = await file.download_as_bytearray()

    pdf_file = io.BytesIO(file_content)
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    except Exception as e:
        logger.error("Error reading PDF: %s", e)
        await update.message.reply_text("تعذر قراءة الملف. تأكد أنه يحتوي على نص قابل للاستخراج.")
        return

    if not text.strip():
        await update.message.reply_text("لم يتم العثور على نص في الملف.")
        return

    await update.message.reply_text("جارٍ الترجمة، يرجى الانتظار...")
    translated = translate_text(text)
    await update.message.reply_text("النص المترجم:\n\n" + translated)

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.MimeType("application/pdf"), handle_document))

    app.run_polling()

if __name__ == '__main__':
    main()
