import os
import asyncio
import fitz  # PyMuPDF
import pdfplumber
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile
from aiogram.filters import Command
from deep_translator import GoogleTranslator

# إنشاء مجلد downloads إذا لم يكن موجودًا
os.makedirs("downloads", exist_ok=True)

TOKEN = "6334414905:AAGdBEBDfiY7W9Nhyml1wHxSelo8gfpENR8"  # استبدل هذا التوكن بتوكن البوت الخاص بك
bot = Bot(token=TOKEN)
dp = Dispatcher()

translator = GoogleTranslator(source="en", target="ar")

async def translate_pdf(input_path, output_path):
    # فتح ملف الـ PDF باستخدام PyMuPDF
    doc = fitz.open(input_path)
    translated_texts = []

    # استخراج النصوص من الملف باستخدام pdfplumber للحفاظ على ترتيب الفقرات
    with pdfplumber.open(input_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                translated_text = translator.translate(text)
                translated_texts.append(translated_text)

    # إعادة إنشاء ملف PDF مع الحفاظ على التصميم وإضافة النصوص المترجمة
    for i, page in enumerate(doc):
        if i < len(translated_texts):
            # إدراج النص المترجم في موضع محدد (يمكنك تعديل الإحداثيات والحجم حسب الحاجة)
            page.insert_text((50, 50), translated_texts[i], fontsize=12, color=(0, 0, 0))

    doc.save(output_path)

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("أرسل لي ملف PDF باللغة الإنجليزية وسأقوم بترجمته إلى العربية مع الحفاظ على تصميمه.")

@dp.message(lambda message: message.document and message.document.mime_type == "application/pdf")
async def handle_pdf(message: types.Message):
    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    input_filename = file.file_path.split('/')[-1]
    input_path = f"downloads/{input_filename}"
    output_path = f"downloads/translated_{input_filename}"

    # تنزيل ملف الـ PDF إلى المجلد downloads
    await bot.download_file(file.file_path, input_path)
    await message.answer("جارٍ ترجمة الملف، انتظر قليلاً...")

    # ترجمة الملف
    await translate_pdf(input_path, output_path)

    translated_file = FSInputFile(output_path, filename="translated.pdf")
    await message.answer_document(translated_file, caption="تمت الترجمة بنجاح!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
