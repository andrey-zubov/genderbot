FROM ubuntu:18.04

RUN mkdir /src
RUN mkdir /static
WORKDIR /src

ENV PYTHONUNBUFFERED 1
ENV C_FORCE_ROOT true
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

RUN apt-get update
RUN echo 'y' | apt-get install python3-pip
RUN echo "y" | apt-get install python3-psycopg2

COPY ./requirements.txt /scripts/
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r /scripts/requirements.txt

