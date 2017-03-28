FROM python:3.6
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE api.config.settings
ENV SECRET_KEY r#lkao5gtpp@me&4532%!q%sj9yzg)xb-_*mlousmi&=#2r7&w
ENV DEBUG True
ENV DATABASE_URL postgres://postgres@db/postgres
ENV DOCKER_HOST True
RUN mkdir /project
WORKDIR /project
RUN apt-get update
RUN apt-get install -y pkg-config libfreetype6-dev libpng12-dev
ADD . /project/
RUN pip install -r requirements.txt
