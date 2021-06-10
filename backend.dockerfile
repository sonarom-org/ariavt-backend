# syntax=docker/dockerfile:1

# Alpine: small distro
FROM python:3.9-slim-buster

WORKDIR /app_wd/

# Copy requirements
COPY requirements.txt requirements.txt
# Install requirements
# apk... : necessary for psycopg2
# Create folder in which the app-data volume will be mounted
RUN apt-get update && \
    apt-get -y install libpq-dev gcc && \
    pip3 install -r requirements.txt

RUN mkdir /mnt/app-data

# Copy
# TODO: se puede mirar de no copiar todo, sino solo lo necesario
COPY . .

