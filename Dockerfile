FROM python:3

WORKDIR /app

COPY kubernetes/worker.py /app
COPY kubernetes/controller.py /app
COPY requirements.txt /app
COPY google_credentials.txt /app

RUN pip3 install --trusted-host pypi.python.org -r requirements.txt
