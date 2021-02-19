FROM python:3.9

LABEL "maintainer" = "Alejandro E. Rendon <alejandro@rendon.co>"

ADD requirements.txt /requirements.txt
ADD entrypoint.sh /entrypoint.sh

RUN pip install -r requirements.txt

ENTRYPOINT ["/entrypoint.sh"]
