# استخدام صورة بايثون خفيفة
FROM python:3.9-slim

# تثبيت ffmpeg اللازم لمعالجة ملفات الصوت عبر pydub
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# تعيين مجلد العمل
WORKDIR /app

# نسخ ملف المتطلبات وتثبيت المكتبات
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ ملفات الكود إلى داخل الحاوية
COPY bot.py .

# تعيين الأمر الافتراضي لتشغيل البوت
CMD ["python", "bot.py"]
