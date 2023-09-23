FROM python:3.8-slim-bullseye

RUN apt-get update
RUN pip install libsass
RUN apt-get update
RUN apt-get install -y python-dev libpq-dev
RUN apt-get install -y gcc

RUN pip install Cmake
RUN pip install wheel setuptools pip --upgrade
# RUN pip install -y python-ldap
RUN pip install psycopg2-binary
RUN pip install psycopg2

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt
RUN pip install pandas

EXPOSE 8069
CMD [ "python", "odoo-bin", "-c", "config.conf", "-u", "all", "-i" , "base" ]