FROM python:3.11.4-alpine
COPY . /app
WORKDIR /app

RUN python3 -m venv /opt/env

RUN pip install pip --upgrade
RUN /opt/venv/bin/pip pip install -r requirements.txt
RUN chmod +x entrypoint.sh
CMD ["/app/entrypoint.sh"]