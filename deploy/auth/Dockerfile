FROM python:3.10-slim-bullseye

ENV PYTHONUNBUFFERED=1 \
    HOME=/app/auth

COPY $HOME/requirements.txt .

RUN apt-get update && \
    apt-get install --no-install-recommends -q -y build-essential && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /root/.cache /usr/share/doc/* && \
    useradd --r --user-group app

COPY $HOME .$HOME

USER app
