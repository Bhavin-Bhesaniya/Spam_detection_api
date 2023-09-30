# Use an official Python runtime as a parent image
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

# Upgrade pip to the latest version
RUN pip install pip --upgrade

COPY requirements.txt /app/


# Install the project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the contents of the local src directory to the working directory in the container
COPY . /app

# Expose port 8000 for your Django application
EXPOSE 8000

# Command to start your Django application (modify this as needed)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]