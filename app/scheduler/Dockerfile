FROM python:3.12

WORKDIR /app

COPY ./db ./db
COPY ./shared_utils ./shared_utils
COPY ./scheduler ./scheduler

RUN pip install -e ./db/
RUN pip install -e ./shared_utils/
RUN pip install --no-cache-dir -r ./scheduler/requirements.txt

ENV PYTHONPATH="/app"
WORKDIR /app/scheduler
CMD ["python", "main.py"]