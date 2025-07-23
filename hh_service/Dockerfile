FROM python:3.12

WORKDIR /app
COPY ./fabric ./fabric
COPY ./hh_service ./hh_service

RUN pip install -e ./fabric/
RUN pip install --no-cache-dir -r ./hh_service/requirements.txt

ENV PYTHONPATH="/app"
WORKDIR /app/hh_service

RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]