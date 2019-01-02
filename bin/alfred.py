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


# DEFINICIÓN DE FUNCIONES

# Función para comprobar si el acceso está autorizado o no
def authenticate_client(bot, client_id):
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
    if authenticate_client(bot, update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text="Alfred a la escucha. ¿Puedo ayudarle con algo?.\n"
                                              "Si necesita ayuda use /help")


# Función opción /help
def help(bot, update):
    if authenticate_client(bot, update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text="Opciones disponibles:\n"
                                                          "  /notes\n"
                                                          "  /films\n"
                                                          "  /restaurants\n"
                                                          "  /recipes (próximamente)\n"
                                                          "  /calendar (próximamente)\n")


# Función opción /notes
def notes(bot, update):
    if authenticate_client(bot, update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text="Gestionar notas:\n"
                                                          "  /notes_list\n"
                                                          "  /notes_add\n"
                                                          "  /notes_remove\n")


# Función opción /notes_list
def notes_list(bot, update):
    if authenticate_client(bot, update.message.chat_id):
        task_list = subprocess.run(["task", "project:notes", "list"], stdout=subprocess.PIPE)
        if task_list.stdout.decode('utf-8') == "":
            bot.send_message(chat_id=update.message.chat_id, text="Notas actuales:\n"
                                                                  "(vacío)")
        else:
            bot.send_message(chat_id=update.message.chat_id, text="Notas actuales:\n" + task_list.stdout.decode('utf-8'))


# Función opción /notes_add
def notes_add(bot, update):
    if authenticate_client(bot, update.message.chat_id):
        task_desc = update.message.text.replace("/notes_add ", "")
        if task_desc == "/notes_add":
            bot.send_message(chat_id=update.message.chat_id, text="Para añadir una nota debe proceder como se indica:\n"
                                                                  "  /notes_add <descripción>")
        else:
            subprocess.run(["task", "project:notes", "add", task_desc], stdout=subprocess.PIPE)
            bot.send_message(chat_id=update.message.chat_id, text="Se ha añadido la siguiente nota:\n" + task_desc)
            logging.info("Alfred añadió la nota " + task_desc + " a petición del client ID " + str(update.message.chat_id))


# Función opción /notes_remove
def notes_remove(bot, update):
    if authenticate_client(bot, update.message.chat_id):
        task_id = update.message.text.replace("/notes_remove ", "")
        if task_id == "/notes_remove":
            bot.send_message(chat_id=update.message.chat_id, text="Para eliminar una nota debe proceder como se indica:\n"
                                                                  "  /notes_remove <ID>")
        else:
            subprocess.run(["task", "project:notes", task_id, "done"], stdout=subprocess.PIPE)
            bot.send_message(chat_id=update.message.chat_id, text="Se ha eliminado la siguiente nota:\n" + task_id)
            logging.info("Alfred eliminó la nota con el ID " + task_id + " a petición del client ID " + str(update.message.chat_id))


# Función opción /films
def films(bot, update):
    if authenticate_client(bot, update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text="Gestionar películas:\n"
                                                              "  /films_list\n"
                                                              "  /films_add\n"
                                                              "  /films_remove\n")


# Función opción /films_list
def films_list(bot, update):
    if authenticate_client(bot, update.message.chat_id):
        task_list = subprocess.run(["task", "project:films", "list"], stdout=subprocess.PIPE)
        if task_list.stdout.decode('utf-8') == "":
            bot.send_message(chat_id=update.message.chat_id, text="Películas actuales:\n"
                                                                  "(vacío)")
        else:
            bot.send_message(chat_id=update.message.chat_id, text="Películas actuales:\n" + task_list.stdout.decode('utf-8'))


# Función opción /films_add
def films_add(bot, update):
    if authenticate_client(bot, update.message.chat_id):
        task_desc = update.message.text.replace("/films_add ", "")
        if task_desc == "/films_add":
            bot.send_message(chat_id=update.message.chat_id, text="Para añadir una película debe proceder como se indica:\n"
                                                                  "  /films_add <descripción>")
        else:
            subprocess.run(["task", "project:films", "add", task_desc], stdout=subprocess.PIPE)
            bot.send_message(chat_id=update.message.chat_id, text="Se ha añadido la siguiente película:\n" + task_desc)
            logging.info("Alfred añadió la película " + task_desc + " a petición del client ID " + str(update.message.chat_id))


# Función opción /films_remove
def films_remove(bot, update):
    if authenticate_client(bot, update.message.chat_id):
        task_id = update.message.text.replace("/films_remove ", "")
        if task_id == "/films_remove":
            bot.send_message(chat_id=update.message.chat_id, text="Para eliminar una película debe proceder como se indica:\n"
                                                                  "  /films_remove <ID>")
        else:
            subprocess.run(["task", "project:films", task_id, "done"], stdout=subprocess.PIPE)
            bot.send_message(chat_id=update.message.chat_id, text="Se ha eliminado la siguiente película:\n" + task_id)
            logging.info("Alfred eliminó la película con el ID " + task_id + " a petición del client ID " + str(update.message.chat_id))


# Función opción /restaurants
def restaurants(bot, update):
    if authenticate_client(bot, update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text="Gestionar restaurantes:\n"
                                                              "  /restaurants_list\n"
                                                              "  /restaurants_add\n"
                                                              "  /restaurants_remove\n")


# Función opción /restaurants_list
def restaurants_list(bot, update):
    if authenticate_client(bot, update.message.chat_id):
        task_list = subprocess.run(["task", "project:restaurants", "list"], stdout=subprocess.PIPE)
        if task_list.stdout.decode('utf-8') == "":
            bot.send_message(chat_id=update.message.chat_id, text="Restaurantes actuales:\n"
                                                                  "(vacío)")
        else:
            bot.send_message(chat_id=update.message.chat_id, text="Restaurantes actuales:\n" + task_list.stdout.decode('utf-8'))


# Función opción /restaurants_add
def restaurants_add(bot, update):
    if authenticate_client(bot, update.message.chat_id):
        task_desc = update.message.text.replace("/re"
                                                "staurants_add ", "")
        if task_desc == "/restaurants_add":
            bot.send_message(chat_id=update.message.chat_id, text="Para añadir un restaurante debe proceder como se indica:\n"
                                                                  "  /restaurants_add <descripción>")
        else:
            subprocess.run(["task", "project:restaurants", "add", task_desc], stdout=subprocess.PIPE)
            bot.send_message(chat_id=update.message.chat_id, text="Se ha añadido el siguiente restaurante:\n" + task_desc)
            logging.info("Alfred añadió el restaurante " + task_desc + " a petición del client ID " + str(update.message.chat_id))


# Función opción /restaurants_remove
def restaurants_remove(bot, update):
    if authenticate_client(bot, update.message.chat_id):
        task_id = update.message.text.replace("/restaurants_remove ", "")
        if task_id == "/restaurants_remove":
            bot.send_message(chat_id=update.message.chat_id, text="Para eliminar un restaurante debe proceder como se indica:\n"
                                                                  "  /restaurants_remove <ID>")
        else:
            subprocess.run(["task", "project:restaurants", task_id, "done"], stdout=subprocess.PIPE)
            bot.send_message(chat_id=update.message.chat_id, text="Se ha eliminado el siguiente resturante:\n" + task_id)
            logging.info("Alfred eliminó el restaurante con el ID " + task_id + " a petición del client ID " + str(update.message.chat_id))


# Función para comandos no conocidos
def unknown(bot, update):
    if authenticate_client(bot, update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text="Lo siento, no conozco esa opción.\n"
                                                          "Si necesita ayuda use /help")


# Función para los errores internos
def error(bot, update, error):
    logging.warning('Update "%s" caused error "%s"', update, error)


# PROGRAMA PRINCIPAL

def main():

    # Carga de fichero de configuración
    script_path = os.path.dirname(sys.argv[0])
    with open(script_path + '/../config/config.json', 'r') as f:
        config = json.load(f)
    log_file = config['DEFAULT']['ALFRED_LOG_FILE']
    log_level = config['DEFAULT']['ALFRED_LOG_LEVEL']
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
