import logging
import io
import requests
import asposepdfcloud
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from asposepdfcloud.apis.pdf_api import PdfApi
from googletrans import Translator  # مكتبة الترجمة

# بيانات المصادقة
TELEGRAM_BOT_TOKEN = "6334414905:AAGdBEBDfiY7W9Nhyml1wHxSelo8gfpENR8"
ASPOSE_CLIENT_ID = "f3f79d5c-4fcf-4fc7-91d9-c63555b9e96e"
ASPOSE_CLIENT_SECRET = "cbe2e688854ae8c34601bacfb59967e4"
# تهيئة Aspose API
pdf_api = PdfApi(ASPOSE_CLIENT_ID, ASPOSE_CLIENT_SECRET)
translator = Translator()

# إعداد تسجيل الأخطاء
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context):
    """رسالة ترحيبية عند بدء المحادثة"""
    await update.message.reply_text("مرحبًا! أرسل لي ملف PDF باللغة الإنجليزية وسأقوم بترجمته إلى العربية.")

async def handle_document(update: Update, context):
    """التعامل مع ملفات PDF"""
    document = update.message.document

    if document.mime_type != "application/pdf":
        await update.message.reply_text("يرجى إرسال ملف PDF فقط.")
        return

    await update.message.reply_text("يتم تحميل الملف...")
    file = await document.get_file()
    file_content = await file.download_as_bytearray()

    pdf_file = io.BytesIO(file_content)

    try:
        # حفظ الملف مؤقتًا باسمه
        filename = document.file_name
        with open(filename, "wb") as f:
            f.write(pdf_file.getvalue())

        # تحميل الملف إلى Aspose Cloud
        response = pdf_api.upload_file(filename, pdf_file.getvalue())
        if response.errors:
            await update.message.reply_text("فشل تحميل الملف إلى Aspose Cloud.")
            return

        # استخراج النص من PDF
        extracted_text = pdf_api.get_text(filename).text

        if not extracted_text:
            await update.message.reply_text("لم يتم العثور على نص للترجمة في الملف.")
            return

        # ترجمة النص إلى العربية
        translated_text = translator.translate(extracted_text, src="en", dest="ar").text

        await update.message.reply_text("النص المترجم:\n\n" + translated_text)
    
    except Exception as e:
        logger.error("خطأ في معالجة الملف: %s", e)
        await update.message.reply_text("حدث خطأ أثناء معالجة الملف.")

def main():
    """تشغيل بوت تليجرام"""
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.MimeType("application/pdf"), handle_document))

    app.run_polling()

if __name__ == '__main__':
    main()
