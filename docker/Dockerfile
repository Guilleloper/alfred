FROM python:3.9.2-buster

ENV BASE_PATH=/alfred

WORKDIR ${BASE_PATH}

RUN apt-get update && apt-get install -y taskwarrior \
  && pip install python-telegram-bot==10.1.0 requests==2.12.4 beautifulsoup4==4.6.0 graphyte==1.4 lxml==4.6.3 --upgrade \
  && groupadd -g 10001 alfred \
  && useradd -g 10001 -u 10001 -d /home/alfred -m -s /usr/sbin/nologin alfred \
  && mkdir ${BASE_PATH}/log

COPY ./bin bin
COPY ./config config
COPY ./data data

ENV TASKRC=data/.taskrc
ENV TASKDATA=data/.task

RUN touch ${TASKRC} \
  && mkdir ${TASKDATA} \
  && chown -R alfred:alfred .

USER alfred:alfred

ENTRYPOINT ["python", "bin/alfred.py"]
