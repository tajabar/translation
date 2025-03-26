import os
import re
import fitz  # PyMuPDF
import speech_recognition as sr
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from pydub import AudioSegment
from vosk import Model, KaldiRecognizer
from word2number import w2n

TOKEN = "5146976580:AAE2yXc-JK6MIHVlLDy-O4YODucS_u7Zq-8"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# تحميل نموذج التعرف على الصوت (تأكد من تحميله إلى مجلد `model`)
MODEL_PATH = "model"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("مجلد النموذج غير موجود! قم بتحميل نموذج Vosk من https://alphacephei.com/vosk/models")

model = Model(MODEL_PATH)

def convert_words_to_numbers(text):
    """تحويل الأرقام المكتوبة بالعربية إلى أرقام رقمية"""
    words = text.split()
    converted_words = []
    for word in words:
        try:
            converted_word = str(w2n.word_to_num(word))  # تحويل الكلمة إلى رقم
        except ValueError:
            converted_word = word  # إذا لم يكن رقماً، أبقه كما هو
        converted_words.append(converted_word)
    return " ".join(converted_words)

def extract_pages_from_pdf(pdf_path, start_page, end_page, output_path):
    """استخراج الصفحات المطلوبة من ملف PDF"""
    doc = fitz.open(pdf_path)
    new_doc = fitz.open()
    
    for page_num in range(start_page - 1, end_page):
        new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

    new_doc.save(output_path)
    new_doc.close()

@dp.message_handler(content_types=types.ContentType.VOICE)
async def handle_voice(message: types.Message):
    """معالجة البصمات الصوتية"""
    voice = await message.voice.download()
    ogg_path = f"{message.from_user.id}.ogg"
    wav_path = f"{message.from_user.id}.wav"

    with open(ogg_path, "wb") as f:
        f.write(voice.getvalue())

    # تحويل الصوت من OGG إلى WAV
    audio = AudioSegment.from_ogg(ogg_path)
    audio.export(wav_path, format="wav")

    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)

    try:
        rec = KaldiRecognizer(model, 16000)
        rec.AcceptWaveform(audio_data.get_wav_data())
        text = rec.Result()

        # تنظيف النص المستخرج
        text = re.sub(r'[\W_]+', ' ', text).strip()
        text = convert_words_to_numbers(text)  # تحويل الكلمات إلى أرقام
        match = re.search(r'(\d+)\s+الى\s+(\d+)', text)

        if match:
            start_page, end_page = int(match.group(1)), int(match.group(2))
            await message.reply(f"تم استخراج الصفحات: {start_page} إلى {end_page}")
            # ستتم معالجة PDF هنا لاحقًا عند استلام ملف
        else:
            await message.reply("لم أستطع استخراج أرقام الصفحات من النص. تأكد من النطق بشكل صحيح.")
    except Exception as e:
        await message.reply(f"حدث خطأ أثناء معالجة الصوت: {str(e)}")

    # تنظيف الملفات المؤقتة
    os.remove(ogg_path)
    os.remove(wav_path)

@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def handle_pdf(message: types.Message):
    """استقبال ملفات PDF"""
    if not message.document.file_name.endswith(".pdf"):
        await message.reply("يرجى إرسال ملف PDF فقط.")
        return

    pdf_path = f"{message.from_user.id}.pdf"
    output_path = f"{message.from_user.id}_split.pdf"

    # تحميل الملف
    file = await bot.get_file(message.document.file_id)
    await bot.download_file(file.file_path, pdf_path)

    # استخراج الصفحات المطلوبة
    try:
        # يمكنك استخدام متغيرات start_page و end_page هنا إذا كانت مخزنة مسبقًا من معالجة الصوت
        extract_pages_from_pdf(pdf_path, 2, 5, output_path)
        await message.reply_document(open(output_path, "rb"), caption="تم استخراج الصفحات المطلوبة!")

    except Exception as e:
        await message.reply(f"حدث خطأ أثناء معالجة PDF: {str(e)}")

    # تنظيف الملفات
    os.remove(pdf_path)
    os.remove(output_path)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
