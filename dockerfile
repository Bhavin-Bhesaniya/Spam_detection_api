FROM python:3.11.4-slim-buster

# Prevent Python from writing .pyc files to disk (equivalent to python -B)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Prevent Python from buffering stdout and stderr (equivalent to python -u)

# Create the /app directory
RUN mkdir /app
WORKDIR /app


# Update the package list and install necessary system packages
RUN apt-get update && apt-get install -y \
    pkg-config \
    libmariadb-dev \
    gcc \
    && apt-get clean


RUN pip install pip --upgrade

COPY requirements.txt /app/

# Install the project dependencies
RUN pip install --no-cache-dir -r requirements.txt


COPY . /app

RUN chmod +x /app/migrate.sh

# Install NLTK and download the required tokenizer models
RUN pip install nltk
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

EXPOSE 8000

ENV DJANGO_SETTINGS_MODULE=spam_mail_project.settings

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]