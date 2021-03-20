FROM python:3.9-alpine

LABEL "maintainer" = "Alejandro E. Rendon <alejandro@rendon.co>"

RUN apt update
RUN apt install build-essential

ADD requirements.txt /requirements.txt
ADD entrypoint.sh /entrypoint.sh

RUN pip install -r requirements.txt

ENTRYPOINT ["/entrypoint.sh"]
