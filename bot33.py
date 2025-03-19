import logging
import os
import tempfile
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from pdfminer.high_level import extract_text
from fpdf import FPDF
import requests

# إعداد المتغيرات (استبدل القيم بالمعلومات الخاصة بك)
TELEGRAM_BOT_TOKEN = '5284087690:AAGwKfPojQ3c-SjCHSIdeog-yN3-4Gpim1Y'
SMARTCAT_API_KEY = '4_SejKMWdEqmPLMGpzZtiuT69A6'
SMARTCAT_PROJECT_ID = '21355320-aee6-4b65-966f-a810e802b81a'
SMARTCAT_BASE_URL = 'https://smartcat.ai'

# إعداد سجل الأحداث
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("مرحباً! أرسل لي ملف PDF لترجمته من الإنجليزية إلى العربية.")

def translate_text_with_smartcat(text: str) -> str:
    """
    ترسل النص إلى Smartcat API لترجمته.
    إذا نجح الطلب يتم استخراج النص المترجم، وإلا يتم إرجاع رسالة خطأ.
    """
    url = f"{SMARTCAT_BASE_URL}/api/integration/v1/document/translate"
    headers = {
        'Authorization': f'Bearer {SMARTCAT_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        "projectId": SMARTCAT_PROJECT_ID,
        "sourceLanguage": "en",
        "targetLanguage": "ar",
        "text": text
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        translated_text = response.json().get('translatedText', '')
    else:
        translated_text = "حدث خطأ أثناء الترجمة"
    
    return translated_text

def create_pdf_from_text(text: str, output_path: str):
    """
    تنشئ ملف PDF جديد من النص المُترجم باستخدام خط يدعم Unicode (DejaVuSans).
    تأكد من وجود ملف "DejaVuSans.ttf" في نفس مجلد السكريبت.
    """
    pdf = FPDF()
    pdf.add_page()
    
    # إضافة خط يدعم Unicode
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
    pdf.set_font("DejaVu", '', 12)
    
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # تقسيم النص إلى أسطر وإضافتها إلى الملف
    lines = text.split('\n')
    for line in lines:
        pdf.multi_cell(0, 10, line)
    
    pdf.output(output_path)

def handle_document(update: Update, context: CallbackContext):
    document = update.message.document
    
    # التأكد من أن الملف هو PDF
    if document.mime_type != 'application/pdf':
        update.message.reply_text("الرجاء إرسال ملف PDF فقط.")
        return

    file = document.get_file()
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tf:
        file.download(custom_path=tf.name)
        pdf_path = tf.name

    update.message.reply_text("تم استلام الملف، جارٍ استخراج النص...")
    
    try:
        # استخراج النص من ملف PDF
        extracted_text = extract_text(pdf_path)
        update.message.reply_text("تم استخراج النص، جارٍ الترجمة...")
        
        # ترجمة النص باستخدام Smartcat API
        translated_text = translate_text_with_smartcat(extracted_text)
        
        # إنشاء ملف PDF جديد يحتوي على النص المترجم
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as out_tf:
            output_pdf_path = out_tf.name
            
        create_pdf_from_text(translated_text, output_pdf_path)
        
        # إرسال الملف المترجم للمستخدم
        update.message.reply_document(document=open(output_pdf_path, 'rb'))
        update.message.reply_text("تمت الترجمة وإرسال الملف المُترجم.")
        
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        update.message.reply_text("حدث خطأ أثناء معالجة الملف.")
    finally:
        # محاولة حذف الملفات المؤقتة
        try:
            os.remove(pdf_path)
            os.remove(output_pdf_path)
        except Exception as cleanup_error:
            logger.warning(f"Error cleaning up temporary files: {cleanup_error}")

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.document, handle_document))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
