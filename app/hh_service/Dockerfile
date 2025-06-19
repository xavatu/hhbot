FROM python:3.12

WORKDIR /app

COPY ./db ./db
COPY ./shared_utils ./shared_utils
COPY ./hh_service ./hh_service

RUN pip install -e ./db/
RUN pip install -e ./shared_utils/
RUN pip install --no-cache-dir -r ./hh_service/requirements.txt

ENV PYTHONPATH="/app"
WORKDIR /app/hh_service
CMD ["python", "main.py"]