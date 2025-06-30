FROM python:3.12

WORKDIR /app
COPY alembic/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["alembic"]
