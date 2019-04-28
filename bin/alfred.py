######################################
# BOT DE TELEGRAM PARA USO DOMÉSTICO #
######################################


# CARGA DE LIBRERÍAS

import logging
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import subprocess
import json
import sys
import os
from modules import mod_birthdays
from modules import mod_events
from modules import mod_amazon


# DEFINICIÓN DE FUNCIONES

# Función para comprobar si el acceso está autorizado o no
def client_authentication(bot, client_id):
    if str(client_id) in client_ids:
        return True
    else:
        bot.send_message(chat_id=client_id,
                         text="Lo siento, pero no estás autorizado para interactuar conmigo. Aún no nos han presentado.\n"
                              ":(")
        logging.warning("Registrado acceso no autorizado del cliente " + str(client_id))
        return False


# Función opción /start
def start(bot, update):
    if client_authentication(bot, update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text="Alfred a la escucha. ¿Puedo ayudarle con algo?.\n"
                                              "Si necesita ayuda use /help")


# Función opción /help
def help(bot, update):
    if client_authentication(bot, update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text="Opciones disponibles:\n"
                                                          "  /amazon\n"
                                                          "  /birthdays\n"
                                                          "  /events\n"
                                                          "  /films\n"
                                                          "  /notes\n"
                                                          "  /recipes (coming soon)\n"
                                                          "  /restaurants\n")


# Función opción /amazon
def amazon(bot, update):
    if client_authentication(bot, update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text="Gestionar seguimiento de productos de Amazon:\n"
                                                              "  /amazon_list\n"
                                                              "  /amazon_detail\n"
                                                              "  /amazon_add\n"
                                                              "  /amazon_remove\n"
                                                              "  <--  /back\n")


# Funciín opción /amazon_list
def amazon_list(bot, update):
    if client_authentication(bot, update.message.chat_id):
        mod_amazon.sort(bot, update)
        mod_amazon.list(bot, update)
        amazon(bot, update)


# Funciín opción /amazon_list
def amazon_detail(bot, update):
    if client_authentication(bot, update.message.chat_id):
        mod_amazon.sort(bot, update)
        mod_amazon.detail(bot, update)
        amazon(bot, update)


# Función opción /amazon_add
def amazon_add(bot, update):
    if client_authentication(bot, update.message.chat_id):
        if mod_amazon.add(bot, update):
            mod_amazon.sort(bot, update)
        amazon(bot, update)


# Función opción /amazon_remove
def amazon_remove(bot, update):
    if client_authentication(bot, update.message.chat_id):
        if mod_amazon.remove(bot, update):
            mod_amazon.sort(bot, update)
        amazon(bot, update)


# Función opicón /birthdays
def birthdays(bot, update):
    if client_authentication(bot, update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text="Gestionar cumpleaños:\n"
                                                              "  /birthdays_list\n"
                                                              "  /birthdays_add\n"
                                                              "  /birthdays_remove\n"
                                                              "  <--  /back\n")


# Función opción /birtdhays_list
def birthdays_list(bot, update):
    if client_authentication(bot, update.message.chat_id):
        mod_birthdays.sort(bot, update)
        mod_birthdays.list(bot, update)
        birthdays(bot, update)


# Función opción /birthdays_add
def birthdays_add(bot, update):
    if client_authentication(bot, update.message.chat_id):
        if mod_birthdays.add(bot, update):
            mod_birthdays.sort(bot, update)
        birthdays(bot, update)


# Función opción /birhtdays_remove
def birthdays_remove(bot, update):
    if client_authentication(bot, update.message.chat_id):
        if mod_birthdays.remove(bot, update):
            mod_birthdays.sort(bot, update)
        birthdays(bot, update)


# Función opción /events
def events(bot, update):
    if client_authentication(bot, update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text="Gestionar eventos y recordatorios:\n"
                                                              "  /events_list\n"
                                                              "  /events_add\n"
                                                              "  /events_edit\n"
                                                              "  /events_remove\n"
                                                              "  <--  /back\n")


# Función opción /events_list
def events_list(bot, update):
    if client_authentication(bot, update.message.chat_id):
        mod_events.sort(bot, update)
        mod_events.list(bot, update)
        events(bot, update)


# Función opción /events_add
def events_add(bot, update):
    if client_authentication(bot, update.message.chat_id):
        if mod_events.add(bot, update):
            mod_events.sort(bot, update)
        events(bot, update)


# Función opción /events_edit
def events_edit(bot, update):
    if client_authentication(bot, update.message.chat_id):
        if mod_events.edit(bot, update):
            mod_events.sort(bot, update)
        events(bot, update)


# Función opción /events_remove
def events_remove(bot, update):
    if client_authentication(bot, update.message.chat_id):
        if mod_events.remove(bot, update):
            mod_events.sort(bot, update)
        events(bot, update)


# Función opción /films
def films(bot, update):
    if client_authentication(bot, update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text="Gestionar películas:\n"
                                                              "  /films_list\n"
                                                              "  /films_add\n"
                                                              "  /films_remove\n"
                                                              "  <--  /back\n")


# Función opción /films_list
def films_list(bot, update):
    if client_authentication(bot, update.message.chat_id):
        task_list = subprocess.run(["task", "project:films", "list"], stdout=subprocess.PIPE)
        if task_list.stdout.decode('utf-8') == "":
            bot.send_message(chat_id=update.message.chat_id, text="Películas actuales:\n"
                                                                  "(vacío)")
        else:
            bot.send_message(chat_id=update.message.chat_id, text="Películas actuales:\n" + task_list.stdout.decode('utf-8'))
        films(bot, update)


# Función opción /films_add
def films_add(bot, update):
    if client_authentication(bot, update.message.chat_id):
        task_desc = update.message.text.replace("/films_add ", "")
        if task_desc == "/films_add":
            bot.send_message(chat_id=update.message.chat_id, text="Para añadir una película debe proceder como se indica:\n"
                                                                  "  /films_add <descripción>")
        else:
            subprocess.run(["task", "project:films", "add", task_desc], stdout=subprocess.PIPE)
            bot.send_message(chat_id=update.message.chat_id, text="Se ha añadido la siguiente película:\n" + task_desc)
            logging.info("Alfred añadió la película " + task_desc + " a petición del client ID " + str(update.message.chat_id))
        films(bot, update)


# Función opción /films_remove
def films_remove(bot, update):
    if client_authentication(bot, update.message.chat_id):
        task_id = update.message.text.replace("/films_remove ", "")
        if task_id == "/films_remove":
            bot.send_message(chat_id=update.message.chat_id, text="Para eliminar una película debe proceder como se indica:\n"
                                                                  "  /films_remove <ID>")
        else:
            subprocess.run(["task", "project:films", task_id, "done"], stdout=subprocess.PIPE)
            bot.send_message(chat_id=update.message.chat_id, text="Se ha eliminado la siguiente película:\n" + task_id)
            logging.info("Alfred eliminó la película con el ID " + task_id + " a petición del client ID " + str(update.message.chat_id))
        films(bot, update)


# Función opción /notes
def notes(bot, update):
    if client_authentication(bot, update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text="Gestionar notas:\n"
                                                          "  /notes_list\n"
                                                          "  /notes_add\n"
                                                          "  /notes_remove\n"
                                                          "  <--  /back\n")


# Función opción /notes_list
def notes_list(bot, update):
    if client_authentication(bot, update.message.chat_id):
        task_list = subprocess.run(["task", "project:notes", "list"], stdout=subprocess.PIPE)
        if task_list.stdout.decode('utf-8') == "":
            bot.send_message(chat_id=update.message.chat_id, text="Notas actuales:\n"
                                                                  "(vacío)")
        else:
            bot.send_message(chat_id=update.message.chat_id, text="Notas actuales:\n" + task_list.stdout.decode('utf-8'))
        notes(bot, update)


# Función opción /notes_add
def notes_add(bot, update):
    if client_authentication(bot, update.message.chat_id):
        task_desc = update.message.text.replace("/notes_add ", "")
        if task_desc == "/notes_add":
            bot.send_message(chat_id=update.message.chat_id, text="Para añadir una nota debe proceder como se indica:\n"
                                                                  "  /notes_add <descripción>")
        else:
            subprocess.run(["task", "project:notes", "add", task_desc], stdout=subprocess.PIPE)
            bot.send_message(chat_id=update.message.chat_id, text="Se ha añadido la siguiente nota:\n" + task_desc)
            logging.info("Alfred añadió la nota " + task_desc + " a petición del client ID " + str(update.message.chat_id))
        notes(bot, update)


# Función opción /notes_remove
def notes_remove(bot, update):
    if client_authentication(bot, update.message.chat_id):
        task_id = update.message.text.replace("/notes_remove ", "")
        if task_id == "/notes_remove":
            bot.send_message(chat_id=update.message.chat_id, text="Para eliminar una nota debe proceder como se indica:\n"
                                                                  "  /notes_remove <ID>")
        else:
            subprocess.run(["task", "project:notes", task_id, "done"], stdout=subprocess.PIPE)
            bot.send_message(chat_id=update.message.chat_id, text="Se ha eliminado la siguiente nota:\n" + task_id)
            logging.info("Alfred eliminó la nota con el ID " + task_id + " a petición del client ID " + str(update.message.chat_id))
        notes(bot, update)


# Función opción /restaurants
def restaurants(bot, update):
    if client_authentication(bot, update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text="Gestionar restaurantes:\n"
                                                              "  /restaurants_list\n"
                                                              "  /restaurants_add\n"
                                                              "  /restaurants_remove\n"
                                                              "  <--  /back\n")


# Función opción /restaurants_list
def restaurants_list(bot, update):
    if client_authentication(bot, update.message.chat_id):
        task_list = subprocess.run(["task", "project:restaurants", "list"], stdout=subprocess.PIPE)
        if task_list.stdout.decode('utf-8') == "":
            bot.send_message(chat_id=update.message.chat_id, text="Restaurantes actuales:\n"
                                                                  "(vacío)")
        else:
            bot.send_message(chat_id=update.message.chat_id, text="Restaurantes actuales:\n" + task_list.stdout.decode('utf-8'))
        restaurants(bot, update)


# Función opción /restaurants_add
def restaurants_add(bot, update):
    if client_authentication(bot, update.message.chat_id):
        task_desc = update.message.text.replace("/restaurants_add ", "")
        if task_desc == "/restaurants_add":
            bot.send_message(chat_id=update.message.chat_id, text="Para añadir un restaurante debe proceder como se indica:\n"
                                                                  "  /restaurants_add <descripción>")
        else:
            subprocess.run(["task", "project:restaurants", "add", task_desc], stdout=subprocess.PIPE)
            bot.send_message(chat_id=update.message.chat_id, text="Se ha añadido el siguiente restaurante:\n" + task_desc)
            logging.info("Alfred añadió el restaurante " + task_desc + " a petición del client ID " + str(update.message.chat_id))
        restaurants(bot, update)


# Función opción /restaurants_remove
def restaurants_remove(bot, update):
    if client_authentication(bot, update.message.chat_id):
        task_id = update.message.text.replace("/restaurants_remove ", "")
        if task_id == "/restaurants_remove":
            bot.send_message(chat_id=update.message.chat_id, text="Para eliminar un restaurante debe proceder como se indica:\n"
                                                                  "  /restaurants_remove <ID>")
        else:
            subprocess.run(["task", "project:restaurants", task_id, "done"], stdout=subprocess.PIPE)
            bot.send_message(chat_id=update.message.chat_id, text="Se ha eliminado el siguiente resturante:\n" + task_id)
            logging.info("Alfred eliminó el restaurante con el ID " + task_id + " a petición del client ID " + str(update.message.chat_id))
        restaurants(bot, update)


# Función para comandos no conocidos
def unknown(bot, update):
    if client_authentication(bot, update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text="Lo siento, no conozco esa opción.\n"
                                                          "Si necesita ayuda use /help")


# Función para los errores internos
def error(update, error):
    logging.warning('Update "%s" caused error "%s"', update, error)


# PROGRAMA PRINCIPAL

def main():

    # Carga de fichero de configuración
    script_path = os.path.dirname(sys.argv[0])
    with open(script_path + '/../config/config.json', 'r') as f:
        config = json.load(f)
    log_file = config['DEFAULT']['LOG_FILE']
    log_level = config['DEFAULT']['LOG_LEVEL']
    bot_token = config['DEFAULT']['BOT_TOKEN']
    global client_ids
    client_ids = config['DEFAULT']['CLIENT_IDS']

    # Configurar logger a fichero
    logging.basicConfig(level=getattr(logging, log_level),
                        format="[%(asctime)s] [%(levelname)s] - [Alfred] - %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                        filename=log_file,
                        filemode='a')

    # Configurar logger a stdout
    console = logging.StreamHandler()
    console.setLevel(getattr(logging, log_level))
    console.setFormatter(logging.Formatter("[%(levelname)s] - [Alfred] - %(message)s"))
    logging.getLogger('').addHandler(console)

    # Inicio
    logging.info("Inicio del programa")

    # Crear el EventHandler para el bot
    updater = Updater(token=bot_token)

    # Obtener el Dispatcher para registrar los Handlers
    dispatcher = updater.dispatcher

    # Añadir al Dispatcher un Handler para el comando /start
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    # Añadir al Dispatcher un Handler para el comando /help
    help_handler = CommandHandler('help', help)
    dispatcher.add_handler(help_handler)

    # Añadir al Dispatcher un Handler para el comando /back
    back_handler = CommandHandler('back', help)
    dispatcher.add_handler(back_handler)

    # Añadir al Dispatcher un Handler para el comando /amazon
    amazon_handler = CommandHandler('amazon', amazon)
    dispatcher.add_handler(amazon_handler)

    # Añadir al Dispatcher un Handler para el comando /amazon_list
    amazon_list_handler = CommandHandler('amazon_list', amazon_list)
    dispatcher.add_handler(amazon_list_handler)

    # Añadir al Dispatcher un Handler para el comando /amazon_detail
    amazon_detail_handler = CommandHandler('amazon_detail', amazon_detail)
    dispatcher.add_handler(amazon_detail_handler)

    # Añadir al Dispatcher un Handler para el comando /amazon_add
    amazon_add_handler = CommandHandler('amazon_add', amazon_add)
    dispatcher.add_handler(amazon_add_handler)

    # Añadir al Dispatcher un Handler para el comando /amazon_remove
    amazon_remove_handler = CommandHandler('amazon_remove', amazon_remove)
    dispatcher.add_handler(amazon_remove_handler)

    # Añadir al Dispatcher un Handler para el comando /birthdays
    birthdays_handler = CommandHandler('birthdays', birthdays)
    dispatcher.add_handler(birthdays_handler)

    # Añadir al Dispatcher un Handler para el comando /birthdays_list
    birthdays_list_handler = CommandHandler('birthdays_list', birthdays_list)
    dispatcher.add_handler(birthdays_list_handler)

    # Añadir al Dispatcher un Handler para el comando /birthdays_add
    birthdays_add_handler = CommandHandler('birthdays_add', birthdays_add)
    dispatcher.add_handler(birthdays_add_handler)

    # Añadir al Dispatcher un Handler para el comando /birthdays_remove
    birthdays_remove_handler = CommandHandler('birthdays_remove', birthdays_remove)
    dispatcher.add_handler(birthdays_remove_handler)

    # Añadir al Dispatcher un Handler para el comando /events
    events_handler = CommandHandler('events', events)
    dispatcher.add_handler(events_handler)

    # Añadir al Dispatcher un Handler para el comando /events_list
    events_list_handler = CommandHandler('events_list', events_list)
    dispatcher.add_handler(events_list_handler)

    # Añadir al Dispatcher un Handler para el comando /events_add
    events_add_handler = CommandHandler('events_add', events_add)
    dispatcher.add_handler(events_add_handler)

    # Añadir al Dispatcher un Handler para el comando /events_edit
    events_edit_handler = CommandHandler('events_edit', events_edit)
    dispatcher.add_handler(events_edit_handler)

    # Añadir al Dispatcher un Handler para el comando /events_remove
    events_remove_handler = CommandHandler('events_remove', events_remove)
    dispatcher.add_handler(events_remove_handler)

    # Añadir al Dispatcher un Handler para el comando /films
    films_handler = CommandHandler('films', films)
    dispatcher.add_handler(films_handler)

    # Añadir al Dispatcher un Handler para el comando /films_list
    films_list_handler = CommandHandler('films_list', films_list)
    dispatcher.add_handler(films_list_handler)

    # Añadir al Dispatcher un Handler para el comando /films_add
    films_add_handler = CommandHandler('films_add', films_add)
    dispatcher.add_handler(films_add_handler)

    # Añadir al Dispatcher un Handler para el comando /films_remove
    films_remove_handler = CommandHandler('films_remove', films_remove)
    dispatcher.add_handler(films_remove_handler)

    # Añadir al Dispatcher un Handler para el comando /notes
    notes_handler = CommandHandler('notes', notes)
    dispatcher.add_handler(notes_handler)

    # Añadir al Dispatcher un Handler para el comando /notes_list
    notes_list_handler = CommandHandler('notes_list', notes_list)
    dispatcher.add_handler(notes_list_handler)

    # Añadir al Dispatcher un Handler para el comando /notes_add
    notes_add_handler = CommandHandler('notes_add', notes_add)
    dispatcher.add_handler(notes_add_handler)

    # Añadir al Dispatcher un Handler para el comando /notes_remove
    notes_remove_handler = CommandHandler('notes_remove', notes_remove)
    dispatcher.add_handler(notes_remove_handler)

    # Añadir al Dispatcher un Handler para el comando /restaurants
    restaurants_handler = CommandHandler('restaurants', restaurants)
    dispatcher.add_handler(restaurants_handler)

    # Añadir al Dispatcher un Handler para el comando /restaurants_list
    restaurants_list_handler = CommandHandler('restaurants_list', restaurants_list)
    dispatcher.add_handler(restaurants_list_handler)

    # Añadir al Dispatcher un Handler para el comando /restaurants_add
    restaurants_add_handler = CommandHandler('restaurants_add', restaurants_add)
    dispatcher.add_handler(restaurants_add_handler)

    # Añadir al Dispatcher un Handler para el comando /restaurants_remove
    restaurants_remove_handler = CommandHandler('restaurants_remove', restaurants_remove)
    dispatcher.add_handler(restaurants_remove_handler)

    # Añadir al Dispatcher un Handler para los comandos desconocidos
    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)

    # Registrar todos los errores
    dispatcher.add_error_handler(error)

    # Arrancar Updater
    updater.start_polling()
    logging.info("Alfred online")
    updater.idle()
    logging.info("Alfred offline")

    # Fin
    logging.info("Fin del programa")


if __name__ == '__main__':
    main()
