FROM python:3.11

# تحديث النظام وتثبيت الحزم الأساسية (git و curl)
RUN apt-get update && apt-get install -y git curl

# سحب ملفات البوت
RUN git clone https://github.com/RepthonArabic/Repthon.git /root/repthon

# الدخول لمجلد البوت
WORKDIR /root/repthon

# تثبيت Node.js وتحديث مدير الحزم
RUN curl -sL https://deb.nodesource.com/setup_20.x | bash -
RUN apt-get install -y nodejs
RUN npm i -g npm

# تثبيت متطلبات البايثون
RUN pip3 install --no-cache-dir -r requirements.txt

ENV PATH="/home/repthon/bin:$PATH"

# أمر تشغيل البوت
CMD ["python3", "-m", "repthon"]
