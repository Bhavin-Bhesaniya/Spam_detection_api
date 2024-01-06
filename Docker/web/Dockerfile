FROM python:3.11.4-slim-buster

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

COPY requirements.txt /app/
RUN pip install pip --upgrade && pip install --no-cache-dir -r /app/requirements.txt

RUN pip install nltk
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords');"

RUN echo "Current Working Directory: $(pwd)"
COPY . /app

EXPOSE 8000
ENV DJANGO_SETTINGS_MODULE=spam_mail_project.settings

CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000"]