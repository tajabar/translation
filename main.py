import os
import asyncio
import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile
from aiogram.filters import Command
from deep_translator import GoogleTranslator

# إعدادات الـ OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # غير هذا المسار حسب نظامك

# إنشاء مجلد downloads إذا لم يكن موجودًا
os.makedirs("downloads", exist_ok=True)

TOKEN = "6334414905:AAGdBEBDfiY7W9Nhyml1wHxSelo8gfpENR8"  # ضع التوكن الخاص بك هنا
bot = Bot(token=TOKEN)
dp = Dispatcher()

translator = GoogleTranslator(source="en", target="ar")

async def extract_text_from_image(image):
    """ استخدام OCR لاستخراج النصوص من صورة """
    text = pytesseract.image_to_string(image, lang="eng")
    return text.strip()

async def translate_pdf_with_ocr(input_path, output_path):
    """ استخراج النصوص عبر OCR، ترجمتها، وإعادة إنشائها في PDF جديد """
    images = convert_from_path(input_path)
    doc = fitz.open(input_path)

    for i, page in enumerate(doc):
        img = images[i]
        extracted_text = await extract_text_from_image(img)

        if extracted_text:
            translated_text = translator.translate(extracted_text)
            page.insert_text((50, 50), translated_text, fontsize=12, color=(0, 0, 0))

    doc.save(output_path)
    return True

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("أرسل لي ملف PDF وسأقوم بترجمته إلى العربية مع الحفاظ على تصميمه.")

@dp.message(lambda message: message.document and message.document.mime_type == "application/pdf")
async def handle_pdf(message: types.Message):
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    input_filename = file.file_path.split('/')[-1]
    input_path = f"downloads/{input_filename}"
    output_path = f"downloads/translated_{input_filename}"

    # تنزيل ملف الـ PDF إلى المجلد downloads
    await bot.download_file(file.file_path, input_path)
    await message.answer("جارٍ استخراج النصوص باستخدام OCR وترجمتها، انتظر قليلاً...")

    # استخدام OCR لاستخراج النصوص وترجمتها
    success = await translate_pdf_with_ocr(input_path, output_path)

    if success:
        translated_file = FSInputFile(output_path, filename="translated.pdf")
        await message.answer_document(translated_file, caption="تمت الترجمة بنجاح باستخدام OCR!")
    else:
        await message.answer("عذرًا، لم أتمكن من استخراج النصوص من هذا الملف.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

