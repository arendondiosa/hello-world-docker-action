FROM python:3.9-slim-buster

LABEL "maintainer" = "Alejandro E. Rendon <alejandro@rendon.co>"

RUN apk update && apk upgrade && \
    apk add --no-cache bash git openssh

ADD requirements.txt /requirements.txt
ADD entrypoint.sh /entrypoint.sh

RUN pip install -r requirements.txt

ENTRYPOINT ["/entrypoint.sh"]
