# alfred
Scripts and documentation referred to the Alfred project

Alfred is a software that manages a personal Telegram Bot. It's based in the python-telegram-bot that provides some methods for managing Telegram bots. -> https://github.com/python-telegram-bot/python-telegram-bot

It's necessary to create a Telegram Bot before deploying this code. -> https://core.telegram.org/bots

The platform is based in the technologies/components related below:

1. Python -> The programming language used for the develop.

Features:
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
