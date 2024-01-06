# Stage 1: Build stage
FROM python:3.11.4-slim-buster AS builder

RUN mkdir /app
WORKDIR /app

RUN apt-get update && \
    apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    libmariadb-dev \
    gcc \
    nano \
    && apt-get clean

RUN ls -l

COPY requirements.txt /app
RUN pip install pip --upgrade && pip install --no-cache-dir -r requirements.txt

# Stage 2: Final stage
FROM python:3.11.4-slim-buster

COPY --from=builder /app /app
WORKDIR /app

RUN apt-get update && \
    apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    libmariadb-dev \
    gcc \
    nano \
    && apt-get clean

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

COPY . /app
RUN pip install nltk
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords');"

EXPOSE 8000
ENV DJANGO_SETTINGS_MODULE=spam_mail_project.settings

CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000"]
