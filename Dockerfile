# syntax=docker/dockerfile:1

# Alpine: small distro
FROM python:3.8-alpine

WORKDIR /app_wd/

# Copy requirements
COPY requirements.txt requirements.txt
# Install requirements
RUN pip3 install -r requirements.txt

# Copy app/ into .
COPY ./app/ .

# Run server
CMD [ "uvicorn", "main:app" , "--reload", "--host", "0.0.0.0", "--reload-dir", "."]

