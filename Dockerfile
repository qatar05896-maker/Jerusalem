FROM python:3.11

# تحديث النظام وتثبيت الأدوات الأساسية
RUN apt-get update && apt-get install -y git curl

# تحديد مسار العمل ونسخ الملفات
COPY . /root/repthon
WORKDIR /root/repthon

# تثبيت Node.js (مطلوب لبعض مكاتب البوت)
RUN curl -sL https://deb.nodesource.com/setup_20.x | bash -
RUN apt-get install -y nodejs
RUN npm i -g npm

# تحديث مكتبة الاتصالات وحل تعارضات الإصدارات
RUN sed -i 's/py-tgcalls==1.0.1/py-tgcalls==2.2.8/g' requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# إضافة المسار للبيئة
ENV PATH="/home/repthon/bin:$PATH"

# تشغيل البوت: نسخ ملف الإعدادات ثم تشغيل المديول الأساسي
# ملاحظة: Fly.io سيمرر الـ Secrets تلقائياً للبوت
CMD cp exampleconfig.py config.py && python3 -m repthon
