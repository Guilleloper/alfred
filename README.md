# alfred
<br/><br/>

## Introduction
Scripts and documentation referred to the Alfred project

Alfred is a software that manages a personal Telegram Bot. It's based in the python-telegram-bot that provides some methods for managing Telegram bots. -> https://github.com/python-telegram-bot/python-telegram-bot

It's necessary to create a Telegram Bot before deploying this code. -> https://core.telegram.org/bots

The platform is based in the technologies/components related below:

- Python -> The programming language used for the develop.
<br/><br/>

## Bot features

Basic module:
- Write the press release
- Update the website
- Contact the media
- Restringed Access control.
- Basic Iteration: /start, /help
- Log Generation for recording the activity.
- Creation of a scoreboard. Is allowed to add, remove or list notes.
- Creation of a list of movies recomendations. Is allowed to add, remove or list films.
- Creation of a list of restaurants recomendations. Is allowed to add, remove or list restaurants.
- Settings by config file.
- Records in the log file for non authorized executions.

Events module:
- Bot sends event notifications.
- Periodic execution by cronfile.
- Events management by Bot's commands.

Birthdays module:
- Bot sends birthdays notifications.
- Periodic execution by cronfile.
- Birthdays management by Bot's commands.

(NEW) Amazon module:
- Periodic execution by cronfile.
- Automatic product's price web scrape.
- Prices storage in a Graphite TSDB (it's necessary to have installed a Graphite server).
- Amazon products management by Bot's commands.
- Get stats products (min, max, avg and last product price).
- Get history prices graph image.
- Bot sends notifications about the reduced products price (real discounts).
<br/><br/>

## Manually deployment: Linux installation

1. Create alfred group and user system:
```
$ sudo groupadd -g 10001 alfred
$ sudo useradd -g 10001 -u 10001 -d /home/alfred -m -s /usr/sbin/nologin alfred
```

2. Install TaskWarrior:
```
$ sudo apt-get install -y taskwarrior
$ sudo runuser -u alfred -- touch /home/alfred/.taskrc
```

3. Install python dependencies:
```
$ sudo pip3.5 install python-telegram-bot --upgrade
$ sudo pip3.5 install requests
$ sudo pip3.5 install beautifulsoup4
$ sudo pip3.5 install graphyte
```

4. Create the software location and place it (choose your own location):
```
$ cd /opt
$ sudo git clone https://github.com/Guilleloper/alfred.git
$ sudo rm -fr alfred/docker
$ sudo chown -R alfred:alfred alfred/
```

5. Prepare the logs location (choose your own location):
```
$ sudo mkdir /var/log/alfred
$ sudo chown alfred:alfred /var/log/alfred
```

6. Configure the logs management by Logrotate (choose your own configuration):
```
$ sudo view /etc/logrotate.d/alfred
~
/var/log/alfred/alfred.log
{
  rotate 60
  daily
  compress
  delaycompress
  copytruncate
  missingok
}
~
* You must consider to configure additional logrotate config files if the Events, Birthdays and Amazon modules have their own different log files.
```

7. Complete the config file with your desired configuration:
```
$ sudo view alfred/config/config.json
...
```

8. Add manually the first events, by editing the appropriate file:
```
$ sudo view /opt/alfred/data/events.json
...
```

9. Add manually the first birthdays, by editing the appropriate file:
```
$ sudo view /opt/alfred/data/birthdays.json
...
```

10. Add manually the first tracked Amazon products, by editing the appropriate file:
```
$ sudo view /opt/alfred/data/amazon.json
...
```

11. Configure the cron file for the periodically execution for the events check and notification:
```
$ sudo view /etc/cron.d/events
~
# Alfred events check and notification
00 10,22 * * * alfred /usr/bin/python3.5 /opt/alfred/bin/modules/mod_events.py
~
```

12. Configure the cron file for the periodically execution for the birthdays check and notification:
```
$ sudo view /etc/cron.d/birthdays
~
# Alfred birthdays check and notification
00 08,20 * * * alfred /usr/bin/python3.5 /opt/alfred/bin/modules/mod_birthdays.py
~
```

13. Configure the cron file for the periodically execution for the amazon price extraction and notification:
```
$ sudo view /etc/cron.d/amazon
~
# Alfred amazon price extraction and notification
00 09,21 * * * alfred /usr/bin/python3.5 /opt/alfred/bin/modules/mod_amazon.py
~
```

14. Configure systemd service, start it and enable it:
```
$ sudo view /lib/systemd/system/alfred.service
~
[Unit]
Description=Alfred, the Telegram Bot
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/bin/python3.5 /opt/alfred/bin/alfred.py
User=alfred
Restart=on-failure
RestartSec=30

[Install]
WantedBy=multi-user.target
~

$ sudo systemctl daemon-reload
$ sudo systemctl start alfred && systemctl enable alfred
```
<br/><br/>

## Manually deployment: Docker installation

0. Prerequisites:
- Docker-CE

1. Create alfred group and user system:
```
$ sudo groupadd -g 10001 alfred
$ sudo useradd -g 10001 -G docker -u 10001 -d /home/alfred -m -s /usr/sbin/nologin alfred
```

2. Download the repository in a temporal place:
```
$ cd /var/tmp
$ git clone https://github.com/Guilleloper/alfred.git
```

3. Prepare the config location (choose your own location):
```
$ sudo mkdir /etc/alfred
$ sudo chown alfred:alfred /etc/alfred
```

4. Complete the config file with your desired configuration:
```
$ sudo cp /var/tmp/alfred/config/config.json /etc/alfred
$ sudo view /etc/alfred/config.json
$ sudo chown alfred:alfred /etc/alfred/config.json
...
```

5. Prepare the data location (choose your own location):
```
$ sudo mkdir /var/lib/alfred
$ sudo chown alfred:alfred /var/lib/alfred
```

6. Add manually the first events, by editing the appropriate file:
```
$ sudo cp /var/tmp/alfred/data/events.json /var/lib/alfred
$ sudo view /var/lib/alfred/events.json
$ sudo chown alfred:alfred /var/lib/alfred/events.json
...
```

7. Add manually the first birthdays, by editing the appropriate file:
```
$ sudo cp /var/tmp/alfred/data/birthdays.json /var/lib/alfred
$ sudo view /var/lib/alfred/birthdays.json
$ sudo chown alfred:alfred /var/lib/alfred/birthdays.json
...
```

8. Add manually the first tracked Amazon products, by editing the appropriate file:
```
$ sudo cp /var/tmp/alfred/data/amazon.json /var/lib/alfred
$ sudo view /var/lib/alfred/amazon.json
$ sudo chown alfred:alfred /var/lib/alfred/amazon.json
...
```

9. Prepare the logs location (choose your own location):
```
$ sudo mkdir /var/log/alfred
$ sudo chown alfred:alfred /var/log/alfred
```

10. Configure the logs management by Logrotate (choose your own configuration):
```
$ sudo view /etc/logrotate.d/alfred
~
/var/log/alfred/alfred.log
{
  rotate 60
  daily
  compress
  delaycompress
  copytruncate
  missingok
}
~
* You must consider to configure additional logrotate config files if the Events, Birthdays and Amazon modules have their own different log files.
```

11. Configure the cron file for the periodically execution for the events check and notification:
```
$ sudo view /etc/cron.d/events
~
# Alfred events check and notification
00 10,22 * * * alfred docker exec alfred python /alfred/bin/modules/mod_events.py >/dev/null
~
```

12. Configure the cron file for the periodically execution for the birthdays check and notification:
```
$ sudo view /etc/cron.d/birthdays
~
# Alfred birthdays check and notification
00 08,20 * * * alfred docker exec alfred python /alfred/bin/modules/mod_birthdays.py >/dev/null
~
```

13. Configure the cron file for the periodically execution for the amazon price extraction and notification:
```
$ sudo view /etc/cron.d/amazon
~
# Alfred amazon price extraction and notification
00 09,21 * * * alfred docker exec alfred python /alfred/bin/modules/mod_amazon.py >/dev/null
~
```

14. Build the Alfred Docker image:
```
$ cd alfred
$ docker build -f docker/Dockerfile -t "alfred:`cat VERSION`" .
```

15. Create Docker container:
```
$ sudo runuser -u alfred -- docker run -d --name alfred \
  -v /etc/timezone:/etc/timezone:ro \
  -v /etc/localtime:/etc/localtime:ro \
  -v /var/lib/alfred:/alfred/data \
  -v /etc/alfred:/alfred/config \
  -v /var/log/alfred:/alfred/log \
  alfred:`cat VERSION`
```

16. Configure systemd service, start it and enable it:
```
$ sudo runuser -u alfred -- docker stop alfred
$ sudo view /lib/systemd/system/alfred.service
~
[Unit]
Description=Alfred, the Telegram Bot
After=docker.service
Wants=network-online.target docker.socket
Requires=docker.socket

[Service]
Type=simple
ExecStart=/usr/bin/docker start -a alfred
ExecStop=/usr/bin/docker stop -t 30 alfred
User=alfred
Restart=on-failure
RestartSec=30

[Install]
WantedBy=multi-user.target
~

$ sudo systemctl daemon-reload
$ sudo systemctl start alfred && systemctl enable alfred
$ cd; rm -fr /var/tmp/alfred
```
<br/><br/>

## Automatically Ansible deployment

(in proccess)