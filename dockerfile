FROM python:3.11.4-alpine

RUN apk update && \
    apk add --no-cache \
    mariadb-dev \
    build-base \
    linux-headers

COPY . /app
WORKDIR /app

RUN python3 -m venv /opt/venv

RUN /opt/venv/bin/pip install pip --upgrade
RUN /opt/venv/bin/pip install -r requirements.txt
RUN chmod +x entrypoint.sh && chmod +x migrate.sh


CMD ["/app/entrypoint.sh"]