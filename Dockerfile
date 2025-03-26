FROM python:3.9-slim

# تثبيت الأدوات اللازمة
RUN apt-get update && \
    apt-get install -y ffmpeg wget unzip && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# تحميل وتثبيت المتطلبات
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# تحميل نموذج Vosk للغة العربية
RUN wget -O vosk-model-ar.zip "https://alphacephei.com/vosk/models/vosk-model-ar-0.22.zip" && \
    unzip vosk-model-ar.zip && \
    mv vosk-model-ar-0.22 model && \
    rm vosk-model-ar.zip

# نسخ الكود إلى الحاوية
COPY bot.py .

CMD ["python", "bot.py"]

