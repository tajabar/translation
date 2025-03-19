# استخدام صورة Python الأساسية
FROM python:3.10

# تعيين مجلد العمل داخل الحاوية
WORKDIR /app

# تحديث pip إلى أحدث إصدار
RUN pip3 install --upgrade pip

# نسخ ملفات المشروع إلى الحاوية
COPY . .

# تثبيت المتطلبات من ملف requirements.txt إذا كان موجودًا
RUN pip3 install --no-cache-dir -r requirements.txt

# تشغيل السكريبت الأساسي عند تشغيل الحاوية
CMD ["python3", "bot.py"]
