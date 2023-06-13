FROM python:3.10-alpine

ENV PYTHONUNBUFFERED=1 \
    HOME=/migrations

COPY $HOME/requirements.txt .

RUN apk add --update --no-cache && \
    apk add musl-dev gcc libpq-dev bash && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

WORKDIR converter

COPY $HOME .$HOME/
COPY alembic.ini ./alembic.ini
COPY app ./app/
