# 1. استخدام نسخة سريعة ومستقرة
FROM python:3.11

# 2. تثبيت الأدوات الأساسية دفعة واحدة (شاملة Node.js وأدوات الميديا)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    wget \
    ffmpeg \
    unzip \
    build-essential \
    imagemagick \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm i -g npm \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 3. تحديد مسار العمل
WORKDIR /root/repthon

# 4. السلاح السري (أداة uv) لتسطيب المكاتب بسرعة البرق
RUN pip install --no-cache-dir uv

# 5. التريك الذكي: نسخ ملف المتطلبات فقط أولاً
COPY requirements.txt .

# 6. تسطيب المكاتب بصاروخ الـ uv (مع إجبار تحديث yt-dlp لأحدث إصدار لحل مشكلة يوتيوب)
RUN sed -i 's/py-tgcalls==1.0.1/py-tgcalls==2.2.8/g' requirements.txt && \
    uv pip install --system --no-cache -r requirements.txt && \
    uv pip install --system --no-cache --upgrade yt-dlp

# 7. نسخ باقي ملفات البوت
COPY . .

# 8. ضبط مسار البيئة بشكل صحيح
ENV PATH="/root/repthon/bin:$PATH"

# 9. تشغيل البوت
CMD ["/bin/bash", "-c", "cp exampleconfig.py config.py && python3 -m repthon"]
