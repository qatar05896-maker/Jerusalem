# 1. استخدام نسخة Python 3.11 المستقرة
FROM python:3.11-slim-bullseye

# 2. تثبيت الأدوات الأساسية (System Dependencies)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    wget \
    ffmpeg \
    unzip \
    build-essential \
    imagemagick \
    libmagic-dev \
    libffi-dev \
    libssl-dev \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 3. تحديد مسار العمل
WORKDIR /root/repthon

# 4. تسطيب أداة uv للسرعة القصوى
RUN pip install --no-cache-dir uv

# 5. نسخ ملف المتطلبات
COPY requirements.txt .

# 6. تسطيب المكاتب (تم إزالة أي إشارة لـ py-tgcalls من هنا)
RUN uv pip install --system --no-cache -r requirements.txt && \
    uv pip install --system --no-cache --upgrade yt-dlp

# 7. نسخ باقي ملفات السورس
COPY . .

# 8. ضبط البيئة والمتغيرات
ENV PATH="/root/repthon/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# 9. تشغيل البوت
CMD ["/bin/bash", "-c", "cp -n exampleconfig.py config.py || true && python3 -m repthon"]
