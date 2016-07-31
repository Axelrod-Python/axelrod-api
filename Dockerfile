FROM python:3.5
ENV PYTHONUNBUFFERED 1
RUN mkdir /project
WORKDIR /project
ADD requirements.txt /project/
RUN apt-get update
RUN apt-get install -y pkg-config libfreetype6-dev libpng12-dev
RUN pip install -r requirements.txt
ADD . /project/
