FROM python:3.9-slim-buster

LABEL "maintainer" = "Alejandro E. Rendon <alejandro@rendon.co>"

RUN apt-get update \
    && apt-get install -y git

ADD requirements.txt /requirements.txt
ADD entrypoint.sh /entrypoint.sh

RUN pip install -r requirements.txt

ENTRYPOINT ["/entrypoint.sh"]
