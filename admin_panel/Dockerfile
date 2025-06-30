FROM python:3.12

WORKDIR /app
COPY ./fabric ./fabric
COPY ./admin_panel ./admin_panel

RUN pip install -e ./fabric/
RUN pip install --no-cache-dir -r ./admin_panel/requirements.txt

ENV PYTHONPATH="/app"
WORKDIR /app/admin_panel

RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]