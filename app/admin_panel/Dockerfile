FROM python:3.12

WORKDIR /app

COPY ./db ./db
COPY ./shared_utils ./shared_utils
COPY ./admin_panel ./admin_panel

RUN pip install -e ./db/
RUN pip install -e ./shared_utils/
RUN pip install --no-cache-dir -r ./admin_panel/requirements.txt

ENV PYTHONPATH="/app"
WORKDIR /app/admin_panel
CMD ["python", "main.py"]