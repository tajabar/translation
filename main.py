import logging
import io
import requests
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import PyPDF2

# إعدادات البوت ومفتاح API الخاص بـ APY Hub
TELEGRAM_BOT_TOKEN = "6334414905:AAGdBEBDfiY7W9Nhyml1wHxSelo8gfpENR8"
API_TOKEN = "APY0ShNmihUEqMaIuecO9MOQJnoWaBmCcLPfDzknG0URVRiDhAjU2HLznsHVkA4tX"
# تم تعديل نقطة النهاية لتشمل "/translate" في نهايتها
TRANSLATOR_ENDPOINT = "https://api.apyhub.com/utility/text-translator/translate"

# إعداد تسجيل الأخطاء
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update, context):
    await update.message.reply_text("مرحباً! أرسل لي ملف PDF باللغة الإنجليزية وسأقوم بترجمته إلى العربية.")

def translate_text(text):
    """
    ترسل هذه الدالة النص إلى API APY Hub لترجمته من الإنجليزية إلى العربية.
    """
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_TOKEN
    }
    data = {
        "text": text,
        "source": "en",
        "target": "ar"
    }
    try:
        response = requests.post(TRANSLATOR_ENDPOINT, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            # تأكد من مفتاح الاستجابة وفقًا لتوثيق APY Hub؛ هنا نفترض أنه "translated_text"
            return result.get("translated_text", "لم يتم العثور على نص مترجم في الاستجابة.")
        else:
            logger.error("خطأ في الترجمة: %s", response.text)
            return f"فشل الاتصال بخدمة الترجمة: {response.text}"
    except Exception as e:
        logger.error("Exception during translation: %s", e)
        return "حدث خطأ أثناء الترجمة."

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
        logger.error("خطأ في قراءة PDF: %s", e)
        await update.message.reply_text("تعذر قراءة الملف. تأكد أنه ملف PDF يحتوي على نص قابل للاستخراج.")
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
