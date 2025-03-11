# استخدام صورة بايثون خفيفة
FROM python:3.9-slim

# تحديد مجلد العمل داخل الحاوية
WORKDIR /app

# نسخ ملف المتطلبات وتثبيت المكتبات
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات التطبيق إلى الحاوية
COPY . .

# تحديد الأمر الذي يشغل البوت (تأكد من أن main.py هو الملف الرئيسي)
CMD ["python", "main.py"]
