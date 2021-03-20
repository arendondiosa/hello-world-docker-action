FROM python:3.9-slim

LABEL "maintainer" = "Alejandro E. Rendon <alejandro@rendon.co>"

RUN apt-get update
RUN apt-get install -y build-essential

ADD requirements.txt /requirements.txt
ADD entrypoint.sh /entrypoint.sh

RUN pip install -r requirements.txt

ENTRYPOINT ["/entrypoint.sh"]
