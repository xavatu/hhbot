FROM python:3.12

WORKDIR /app
COPY ./tgbot ./tgbot

RUN pip install --no-cache-dir -r ./tgbot/requirements.txt

ENV PYTHONPATH="/app"
WORKDIR /app/tgbot