FROM python:3.10

WORKDIR /usr/app

COPY requirements.txt ./
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt
COPY ./backend/ .

EXPOSE 8000