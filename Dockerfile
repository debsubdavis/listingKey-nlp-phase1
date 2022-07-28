# syntax=docker/dockerfile:1

FROM python:slim-buster

ADD src/app.py .

RUN pip install --upgrade pip

COPY requirements.txt requirements.txt
RUN pip install -U -r requirements.txt
RUN python -m spacy download en_core_web_sm