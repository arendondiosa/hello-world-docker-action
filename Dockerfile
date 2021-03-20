FROM python:3.9-alpine

LABEL "maintainer" = "Alejandro E. Rendon <alejandro@rendon.co>"

RUN apk add --update build-essential

ADD requirements.txt /requirements.txt
ADD entrypoint.sh /entrypoint.sh

RUN pip install -r requirements.txt

ENTRYPOINT ["/entrypoint.sh"]
