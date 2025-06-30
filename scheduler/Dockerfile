FROM python:3.12

WORKDIR /app
COPY ./fabric ./fabric
COPY ./scheduler ./scheduler

RUN pip install -e ./fabric/
RUN pip install --no-cache-dir -r ./scheduler/requirements.txt

ENV PYTHONPATH="/app"
WORKDIR /app/scheduler

RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]