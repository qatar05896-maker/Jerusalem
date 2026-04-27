FROM python:3.11

RUN apt-get update && apt-get install -y git curl

# بما إن Fly.io بيسحب الكود مباشرة، مش محتاجين git clone هنا
# هننسخ الملفات الموجودة في الريبو للفولدر اللي هيشتغل منه البوت
COPY . /root/repthon
WORKDIR /root/repthon

RUN curl -sL https://deb.nodesource.com/setup_20.x | bash -
RUN apt-get install -y nodejs
RUN npm i -g npm

RUN sed -i 's/py-tgcalls==1.0.1/py-tgcalls==2.2.8/g' requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

ENV PATH="/home/repthon/bin:$PATH"

# هنا التعديل السحري: هنخلي البوت يعتمد على ملف config.py
# ونكتب أمر برمجي بسيط بياخد الـ Secrets من النظام ويحطها في الملف
CMD cp exampleconfig.py config.py && \
    sed -i "s|DB_URI = \"رابـط التخـزين الخـاص بك\"|DB_URI = \"$DB_URI\"|g" config.py && \
    sed -i "s|APP_ID = 6|APP_ID = $APP_ID|g" config.py && \
    sed -i "s|API_HASH = \"ضع كود الايبي هاش\"|API_HASH = \"$API_HASH\"|g" config.py && \
    sed -i "s|STRING_SESSION = \"كود تيرمــكس\"|STRING_SESSION = \"$STRING_SESSION\"|g" config.py && \
    sed -i "s|TG_BOT_TOKEN = \"توكـن البـوت الخـاص بك\"|TG_BOT_TOKEN = \"$TG_BOT_TOKEN\"|g" config.py && \
    sed -i "s|PRIVATE_GROUP_BOT_API_ID = \"-100\"|PRIVATE_GROUP_BOT_API_ID = \"$PRIVATE_GROUP_BOT_API_ID\"|g" config.py && \
    sed -i "s|ALIVE_NAME = \"اسم حسابك التلي\"|ALIVE_NAME = \"$ALIVE_NAME\"|g" config.py && \
    python3 -m repthon
