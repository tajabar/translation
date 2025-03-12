import logging
import io
import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import PyPDF2

# إعدادات البوت ومفتاح الترجمة
TELEGRAM_BOT_TOKEN = "6334414905:AAGdBEBDfiY7W9Nhyml1wHxSelo8gfpENR8"
YANDEX_API_KEY = "aje8gi5i95c2mra75nub"
YANDEX_TRANSLATE_URL = "https://translate.yandex.net/api/v1.5/tr.json/translate"

# إعداد تسجيل الأخطاء (اختياري)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update, context):
    update.message.reply_text("مرحباً! أرسل لي ملف PDF يحتوي على نص باللغة الإنجليزية وسأقوم بترجمته إلى العربية.")

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
            # النص المترجم يُعاد في قائمة ضمن المفتاح 'text'
            return " ".join(data["text"])
        else:
            return "حدث خطأ أثناء الترجمة. رمز الخطأ: {}".format(data.get("code"))
    except Exception as e:
        logger.error("Error during translation: %s", e)
        return "فشل الاتصال بخدمة الترجمة."

def handle_document(update, context):
    document = update.message.document
    if document.mime_type != "application/pdf":
        update.message.reply_text("يرجى إرسال ملف PDF.")
        return

    update.message.reply_text("يتم تحميل الملف ومعالجته...")
    file = document.get_file()
    file_content = file.download_as_bytearray()

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
        update.message.reply_text("تعذر قراءة الملف. تأكد أنه ملف PDF يحتوي على نص قابل للاستخراج.")
        return

    if not text.strip():
        update.message.reply_text("لم يتم العثور على نص في الملف.")
        return

    update.message.reply_text("جارٍ الترجمة، يرجى الانتظار...")
    translated = translate_text(text)
    update.message.reply_text("النص المترجم:\n\n" + translated)

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document.mime_type("application/pdf"), handle_document))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
