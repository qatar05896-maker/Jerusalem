# 1. استخدام نسخة مصغرة وسريعة جداً للتحميل
FROM python:3.11

# 2. تثبيت الأدوات الأساسية دفعة واحدة وتنظيف الكاش لتقليل المساحة
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ffmpeg \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm i -g npm \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 3. تحديد مسار العمل
WORKDIR /root/repthon

# 4. السلاح السري (أداة uv) لتسطيب المكاتب بسرعة البرق
RUN pip install --no-cache-dir uv

# 5. التريك الذكي: نسخ ملف المتطلبات فقط أولاً (لتفعيل الكاش السريع)
COPY requirements.txt .

# 6. حل التعارضات وتسطيب المكاتب بصاروخ الـ uv
RUN sed -i 's/py-tgcalls==1.0.1/py-tgcalls==2.2.8/g' requirements.txt && \
    uv pip install --system --no-cache -r requirements.txt

# 7. نسخ باقي ملفات البوت (الآن الرفع سيكون في ثواني)
COPY . .

# 8. إضافة المسار للبيئة
ENV PATH="/home/repthon/bin:$PATH"

# 9. تشغيل البوت
CMD ["/bin/bash", "-c", "cp exampleconfig.py config.py && python3 -m repthon"]
