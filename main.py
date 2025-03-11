import os
import asyncio
import fitz  # PyMuPDF
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile
from aiogram.filters import Command
from deep_translator import GoogleTranslator

# إنشاء مجلد downloads إذا لم يكن موجودًا
os.makedirs("downloads", exist_ok=True)

TOKEN = "6334414905:AAGdBEBDfiY7W9Nhyml1wHxSelo8gfpENR8"  # استبدل هذا بالتوكن الخاص بك
bot = Bot(token=TOKEN)
dp = Dispatcher()

translator = GoogleTranslator(source="en", target="ar")

async def extract_text_from_pdf(input_path):
    """ استخراج النصوص من ملف PDF """
    doc = fitz.open(input_path)
    extracted_text = []

    for page in doc:
        text = page.get_text("text", sort=True).strip()  # استخراج النصوص مع ترتيبها الصحيح
        if text:
            extracted_text.append(text)

    return extracted_text

async def translate_pdf(input_path, output_path):
    """ ترجمة النصوص وإعادة إنشائها في PDF جديد """
    extracted_text = await extract_text_from_pdf(input_path)

    if not extracted_text:
        return False  # لا يوجد نص مستخرج للترجمة

    translated_texts = [translator.translate(text) for text in extracted_text]

    # إنشاء PDF جديد مع النصوص المترجمة
    doc = fitz.open()
    for translated_text in translated_texts:
        page = doc.new_page()
        page.insert_text((50, 50), translated_text, fontsize=12, color=(0, 0, 0))

    doc.save(output_path)
    return True

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
    await message.answer("جارٍ استخراج النصوص وترجمتها، انتظر قليلاً...")

    # ترجمة الملف
    success = await translate_pdf(input_path, output_path)

    if success:
        translated_file = FSInputFile(output_path, filename="translated.pdf")
        await message.answer_document(translated_file, caption="تمت الترجمة بنجاح!")
    else:
        await message.answer("عذرًا، لم أتمكن من استخراج النصوص من هذا الملف.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
