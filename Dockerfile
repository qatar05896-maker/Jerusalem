FROM repthonarabic/repthon:slim-buster

RUN git clone https://github.com/RepthonArabic/Repthon.git /root/repthon

WORKDIR /root/repthon

RUN curl -sL https://deb.nodesource.com/setup_20.x | bash -
RUN apt-get install -y nodejs
RUN npm i -g npm
RUN pip3 install --no-cache-dir -r requirements.txt

ENV PATH="/home/repthon/bin:$PATH"

CMD ["python3","-m","repthon"]
