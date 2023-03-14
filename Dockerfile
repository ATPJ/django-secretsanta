FROM python:3.11.2-slim
MAINTAINER ATPJ

ENV PYTHONUNBUFFERED 1

COPY ./requirements.py /requirements.py
RUN pip install -r /requirements.py

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN adduser user
USER user

