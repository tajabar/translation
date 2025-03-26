import logging
import os
import re
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
import speech_recognition as sr
from pydub import AudioSegment
import PyPDF2

# ضع توكن البوت الخاص بك هنا
TOKEN = '5146976580:AAE2yXc-JK6MIHVlLDy-O4YODucS_u7Zq-8'

# إعداد تسجيل الأحداث
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# مسار ملف PDF المستلم
pdf_file_path = None

def word_to_number(word):
    """
    تحويل الكلمات الترتيبية إلى أرقام.
    """
    mapping = {
        'اولى': 1, 'اول': 1, 'واحد': 1,
        'الثانية': 2, 'ثانيه': 2, 'اثنين': 2,
        'الثالثة': 3, 'ثالثه': 3, 'ثلاثة': 3,
        'الرابعة': 4, 'رابعه': 4, 'اربعة': 4,
        'الخامسة': 5, 'خامسه': 5, 'خمسة': 5,
        'السادسة': 6, 'سادسه': 6, 'ستة': 6,
        'السابعة': 7, 'سابعه': 7, 'سبعة': 7,
        'الثامنة': 8, 'تامنه': 8, 'ثمانية': 8,
        'التاسعة': 9, 'تاسعه': 9, 'تسعة': 9,
        'العاشرة': 10, 'عاشره': 10, 'عشرة': 10
    }
    word = word.lower().strip()
    # إزالة لاحقة "ال" إن وجدت
    if word.startswith("ال"):
        word = word[2:]
    return mapping.get(word, None)

def start(update, context):
    update.message.reply_text("مرحباً! أرسل ملف PDF أولاً.")

def handle_pdf(update, context):
    global pdf_file_path
    file = update.message.document.get_file()
    pdf_file_path = 'input.pdf'
    file.download(pdf_file_path)
    update.message.reply_text("تم استلام ملف PDF. الآن أرسل بصمة صوتية تحتوي على التعليمات.")

def handle_voice(update, context):
    global pdf_file_path
    if not pdf_file_path:
        update.message.reply_text("لم يتم استلام ملف PDF بعد. أرجو إرساله أولاً.")
        return

    # تحميل ملف الصوت
    voice = update.message.voice.get_file()
    voice_file_path = "voice.ogg"
    voice.download(voice_file_path)

    # تحويل ملف ogg إلى wav باستخدام pydub
    wav_file_path = "voice.wav"
    try:
        audio = AudioSegment.from_ogg(voice_file_path)
        audio.export(wav_file_path, format="wav")
    except Exception as e:
        update.message.reply_text("حدث خطأ أثناء تحويل ملف الصوت.")
        return

    # التعرف على الكلام باستخدام SpeechRecognition
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_file_path) as source:
        audio_data = recognizer.record(source)
    try:
        # تحديد اللغة العربية (ar-SA)
        text = recognizer.recognize_google(audio_data, language="ar-SA")
        update.message.reply_text(f"تم التعرف على النص: {text}")
    except Exception as e:
        update.message.reply_text("حدث خطأ أثناء التعرف على الصوت.")
        return

    # استخراج أرقام الصفحات من النص مع دعم الكلمات الترتيبية
    # يبحث التعبير العادي عن "صفحه" ثم الكلمة المراد تحويلها، ثم "الى صفحه" ثم الكلمة الثانية
    match = re.search(r'(?:صفحه\s+)?([^\s]+)\s+الى\s+(?:صفحه\s+)?([^\s]+)', text, re.IGNORECASE)
    if not match:
        update.message.reply_text("لم أستطع استخراج أرقام الصفحات من النص. تأكد من النطق بشكل صحيح.")
        return

    start_str = match.group(1)
    end_str = match.group(2)

    # محاولة تحويل النص إلى رقم مباشرةً، وإن لم يكن رقمًا تحويله باستخدام دالة word_to_number
    try:
        start_page = int(start_str)
    except ValueError:
        start_page = word_to_number(start_str)

    try:
        end_page = int(end_str)
    except ValueError:
        end_page = word_to_number(end_str)

    if start_page is None or end_page is None:
        update.message.reply_text("لم أستطع تحويل الكلمات إلى أرقام. تأكد من النطق.")
        return

    # معالجة ملف PDF واستخراج الصفحات المطلوبة
    try:
        with open(pdf_file_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            writer = PyPDF2.PdfWriter()
            total_pages = len(reader.pages)
            if start_page < 1 or end_page > total_pages or start_page > end_page:
                update.message.reply_text("أرقام الصفحات غير صحيحة. تأكد من أن الصفحات ضمن نطاق الملف.")
                return
            for i in range(start_page - 1, end_page):
                writer.add_page(reader.pages[i])
            output_pdf_path = "output.pdf"
            with open(output_pdf_path, 'wb') as out_pdf:
                writer.write(out_pdf)
        update.message.reply_text("تم استخراج الصفحات المطلوبة، جارٍ إرسال الملف...")
        update.message.reply_document(document=open(output_pdf_path, 'rb'))
    except Exception as e:
        update.message.reply_text("حدث خطأ أثناء معالجة ملف PDF.")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    # استقبال ملف PDF عند إرساله
    dp.add_handler(MessageHandler(Filters.document.pdf, handle_pdf))
    # استقبال الرسائل الصوتية
    dp.add_handler(MessageHandler(Filters.voice, handle_voice))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
