import os
import re
from num2words import num2words
import speech_recognition as sr
from pydub import AudioSegment
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from PyPDF2 import PdfFileReader, PdfFileWriter

# Dictionary to store user PDFs (key: user_id, value: file path)
user_pdfs = {}

# Initialize recognizer
recognizer = sr.Recognizer()

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("مرحبًا! أرسل ملف PDF أولًا، ثم أرسل أمرًا صوتيًا مثل 'قسم من صفحة 6 إلى 12'.")

def handle_pdf(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    pdf_file = update.message.document.get_file()
    pdf_path = f"{user_id}_input.pdf"
    pdf_file.download(pdf_path)
    user_pdfs[user_id] = pdf_path
    update.message.reply_text("تم استلام الملف. الآن أرسل أمرًا صوتيًا لتقسيم الصفحات.")

def convert_written_numbers(text):
    """Convert written numbers (e.g., 'ستة') to digits (e.g., '6')."""
    number_map = {
        "واحد": "1",
        "اثنين": "2",
        "ثلاثة": "3",
        "أربعة": "4",
        "خمسة": "5",
        "ستة": "6",
        "سبعة": "7",
        "ثمانية": "8",
        "تسعة": "9",
        "عشرة": "10",
    }
    for word, digit in number_map.items():
        text = text.replace(word, digit)
    return text

def handle_voice(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if user_id not in user_pdfs:
        update.message.reply_text("يرجى إرسال ملف PDF أولًا!")
        return

    # Download voice message
    voice_file = update.message.voice.get_file()
    ogg_path = f"{user_id}_voice.ogg"
    wav_path = f"{user_id}_voice.wav"
    voice_file.download(ogg_path)

    # Convert OGG to WAV
    audio = AudioSegment.from_ogg(ogg_path)
    audio.export(wav_path, format="wav")

    # Speech-to-text
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language='ar-AR')
            update.message.reply_text(f"تم فهم النص: {text}")
        except sr.UnknownValueError:
            update.message.reply_text("عذراً، لا استطيع فهم الصوت.")
            os.remove(ogg_path)
            os.remove(wav_path)
            return

    # Convert written numbers to digits
    text = convert_written_numbers(text.lower())

    # Extract page numbers using an improved regex
    match = re.search(r'(?:من\s+)?(?:الصفحة\s+)?(\d+)\s+(?:الى|إلى)\s+(\d+)', text, re.IGNORECASE)
    if not match:
        update.message.reply_text("الصيغة غير صحيحة. الرجاء قول شيء مثل: 'قسم من صفحة 6 إلى 12'.")
        os.remove(ogg_path)
        os.remove(wav_path)
        return

    start_page = int(match.group(1)) - 1  # PDFs are 0-indexed
    end_page = int(match.group(2)) - 1

    # Split PDF
    pdf_path = user_pdfs[user_id]
    output_pdf = f"{user_id}_output.pdf"
    split_pdf(pdf_path, start_page, end_page, output_pdf)

    # Send result
    with open(output_pdf, 'rb') as f:
        update.message.reply_document(document=f)

    # Clean up
    os.remove(ogg_path)
    os.remove(wav_path)
    os.remove(output_pdf)

def split_pdf(input_path, start, end, output_path):
    reader = PdfFileReader(input_path)
    writer = PdfFileWriter()
    for page_num in range(start, end + 1):
        if page_num >= reader.getNumPages():
            break
        writer.addPage(reader.getPage(page_num))
    with open(output_path, 'wb') as out:
        writer.write(out)

def main() -> None:
    updater = Updater("5146976580:AAE2yXc-JK6MIHVlLDy-O4YODucS_u7Zq-8")
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.document.pdf, handle_pdf))
    dispatcher.add_handler(MessageHandler(Filters.voice, handle_voice))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
