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
from shutil import copyfile


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


# Función para ordenar el fichero de eventos
def events_sort():
    script_path = os.path.dirname(sys.argv[0])
    with open(script_path + events_file, 'r') as f1:
        events = json.load(f1)
    events_new = {}
    events_new['events'] = []
    event_id_new = 1
    for event in events['events']:
        title = event['title']
        event_date = event['event_date']
        reminder_date = event['reminder_date']
        events_new['events'].append({
            'id': event_id_new,
            'title': title,
            'event_date': event_date,
            'reminder_date': reminder_date
        })
        event_id_new += 1

    # Comprobar si ha habido cambios en la ordenacion de las tareas y reordenar si aplica
    if events != events_new:
        with open(script_path + events_tmp_file, 'w+') as f2:
            json.dump(events_new, f2, indent=2)
        copyfile(script_path + events_tmp_file, script_path + events_file)
        os.remove(script_path + events_tmp_file)
        return True
    else:
        return False


# Función para comprobar si existe un evento con un ID determinado
def event_id_hit(event_id):
    script_path = os.path.dirname(sys.argv[0])
    with open(script_path + events_file, 'r') as f1:
        events = json.load(f1)
    for event in events['events']:
        if int(event_id) == event['id']:
            return True
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
                                                          "  /events\n"
                                                          "  /films\n"
                                                          "  /notes\n"
                                                          "  /recipes (coming soon)\n"
                                                          "  /restaurants\n")


# Función opción /notes
def notes(bot, update):
    if client_authentication(bot, update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text="Gestionar notas:\n"
                                                          "  /notes_list\n"
                                                          "  /notes_add\n"
                                                          "  /notes_remove\n")


# Función opción /notes_list
def notes_list(bot, update):
    if client_authentication(bot, update.message.chat_id):
        task_list = subprocess.run(["task", "project:notes", "list"], stdout=subprocess.PIPE)
        if task_list.stdout.decode('utf-8') == "":
            bot.send_message(chat_id=update.message.chat_id, text="Notas actuales:\n"
                                                                  "(vacío)")
        else:
            bot.send_message(chat_id=update.message.chat_id, text="Notas actuales:\n" + task_list.stdout.decode('utf-8'))


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


# Función opción /films
def films(bot, update):
    if client_authentication(bot, update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text="Gestionar películas:\n"
                                                              "  /films_list\n"
                                                              "  /films_add\n"
                                                              "  /films_remove\n")


# Función opción /films_list
def films_list(bot, update):
    if client_authentication(bot, update.message.chat_id):
        task_list = subprocess.run(["task", "project:films", "list"], stdout=subprocess.PIPE)
        if task_list.stdout.decode('utf-8') == "":
            bot.send_message(chat_id=update.message.chat_id, text="Películas actuales:\n"
                                                                  "(vacío)")
        else:
            bot.send_message(chat_id=update.message.chat_id, text="Películas actuales:\n" + task_list.stdout.decode('utf-8'))


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


# Función opción /restaurants
def restaurants(bot, update):
    if client_authentication(bot, update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text="Gestionar restaurantes:\n"
                                                              "  /restaurants_list\n"
                                                              "  /restaurants_add\n"
                                                              "  /restaurants_remove\n")


# Función opción /restaurants_list
def restaurants_list(bot, update):
    if client_authentication(bot, update.message.chat_id):
        task_list = subprocess.run(["task", "project:restaurants", "list"], stdout=subprocess.PIPE)
        if task_list.stdout.decode('utf-8') == "":
            bot.send_message(chat_id=update.message.chat_id, text="Restaurantes actuales:\n"
                                                                  "(vacío)")
        else:
            bot.send_message(chat_id=update.message.chat_id, text="Restaurantes actuales:\n" + task_list.stdout.decode('utf-8'))


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


# Función opción /events
def events(bot, update):
    if client_authentication(bot, update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text="Gestionar eventos y recordatorios:\n"
                                                              "  /events_list\n"
                                                              "  /events_add\n"
                                                              "  /events_edit\n"
                                                              "  /events_remove\n")


# Función opción /events_list
def events_list(bot, update):
    if client_authentication(bot, update.message.chat_id):
        if events_sort():
            bot.send_message(chat_id=update.message.chat_id, text="Se ha reordenado la lista de eventos")
            logging.info("Lista de eventos reordenada")
        script_path = os.path.dirname(sys.argv[0])
        with open(script_path + events_file, 'r') as f:
            events = json.load(f)
        if events == "":
            bot.send_message(chat_id=update.message.chat_id, text="Eventos actuales:\n"
                                                                  "(vacío)")
        else:
            bot.send_message(chat_id=update.message.chat_id, text="Eventos actuales:\n")
            for event in events['events']:
                id = event['id']
                title = event['title']
                event_date = event['event_date']
                reminder_date = event['reminder_date']
                bot.send_message(chat_id=update.message.chat_id, text="  ID: " + str(id) + "\n"
                                                                      "  Evento: " + title + "\n"
                                                                      "  Fecha: " + event_date + "\n"
                                                                      "  Avisar a partir de: " + reminder_date + "\n")


# Función opción /events_add
def events_add(bot, update):
    if client_authentication(bot, update.message.chat_id):
        logging.debug("Realizando comprobaciones previas antes de crear un evento")
        params = update.message.text.replace("/events_add ", "")
        if params == "/events_add":
            bot.send_message(chat_id=update.message.chat_id, text="Para añadir un evento debe proceder como se indica:\n"
                                                                  "  /events_add <evento> <fecha de evento> <fecha de recordatorio>\n"
                                                                  "  (las fechas en formato DD.MM.AAAA)")
            return False
        if len(params.split(" ")) < 3:
            bot.send_message(chat_id=update.message.chat_id,
                             text="Sintanxis incorrecta. Para añadir un evento debe proceder como se indica:\n"
                                  "  /events_add <evento> <fecha de evento> <fecha de recordatorio>\n"
                                  "  (las fechas en formato DD.MM.AAAA)")
            logging.warning("Sintaxis incorrecta al intentar crear un evento a petición del cliente ID " + str(
            update.message.chat_id))
            return False
        reminder_date_new = params[-10:]
        event_date_new = params[-21:-11]
        title_new = params[:-22]
        if len(event_date_new) != 10:
            bot.send_message(chat_id=update.message.chat_id,
                             text="La fecha de evento debe ir en formato DD.MM.AAAA")
            logging.warning("Se ha introducido mal la fecha de evento al intentar crear un evento a petición del cliente ID " + str(
            update.message.chat_id))
            return False
        if len(event_date_new.split(".")) != 3:
            bot.send_message(chat_id=update.message.chat_id,
                             text="La fecha de evento debe ir en formato DD.MM.AAAA")
            logging.warning("Se ha introducido mal la fecha de evento al intentar crear un evento a petición del cliente ID " + str(
            update.message.chat_id))
            return False
        if len(reminder_date_new) != 10:
            bot.send_message(chat_id=update.message.chat_id,
                             text="La fecha de recordatorio debe ir en formato DD.MM.AAAA")
            logging.warning("Se ha introducido mal la fecha de recordatorio al intentar crear un evento a petición del cliente ID " + str(
            update.message.chat_id))
            return False
        if len(reminder_date_new.split(".")) != 3:
            bot.send_message(chat_id=update.message.chat_id,
                             text="La fecha de recordatorio debe ir en formato DD.MM.AAAA")
            logging.warning("Se ha introducido mal la fecha de recordatorio al intentar crear un evento a petición del cliente ID " + str(
            update.message.chat_id))
            return False
        logging.debug("Creando un nuevo evento")
        script_path = os.path.dirname(sys.argv[0])
        with open(script_path + events_file, 'r') as f1:
            events = json.load(f1)
        events_new = {}
        events_new['events'] = []
        for event in events['events']:
            id = event['id']
            title = event['title']
            event_date = event['event_date']
            reminder_date = event['reminder_date']
            events_new['events'].append({
                'id': id,
                'title': title,
                'event_date': event_date,
                'reminder_date': reminder_date
            })
        id_new = id + 1
        events_new['events'].append({
            'id': id_new,
            'title': title_new,
            'event_date': event_date_new,
            'reminder_date': reminder_date_new
        })
        with open(script_path + events_tmp_file, 'w+') as f2:
            json.dump(events_new, f2, indent=2)
        copyfile(script_path + events_tmp_file, script_path + events_file)
        os.remove(script_path + events_tmp_file)
        bot.send_message(chat_id=update.message.chat_id,
                         text="Se ha creado el evento " + title_new + " con el ID " + str(id_new))
        logging.info("Alfred creó el evento " + title_new + " con el ID " + str(id_new) + " a petición del client ID " + str(
            update.message.chat_id))
        return True


# Función opción /events_edit
def events_edit(bot, update):
    if client_authentication(bot, update.message.chat_id):
        logging.debug("Realizando comprobaciones previas antes de modificar un evento")
        params = update.message.text.replace("/events_edit ", "")
        if params == "/events_edit":
            bot.send_message(chat_id=update.message.chat_id, text="Para modificar un evento debe proceder como se indica:\n"
                                                                  "  /events_edit <ID> <nueva fecha de evento> <nueva fecha de recordatorio>\n"
                                                                  "  (las fechas en formato DD.MM.AAAA)")
            return False
        if len(params.split(" ")) < 3:
            bot.send_message(chat_id=update.message.chat_id,
                             text="Sintanxis incorrecta. Para modificar un evento debe proceder como se indica:\n"
                                  "  /events_edit <ID> <nueva fecha de evento> <nueva fecha de recordatorio>\n"
                                  "  (las fechas en formato DD.MM.AAAA)")
            logging.warning("Sintaxis incorrecta al intentar modificar un evento")
            return False
        reminder_date_new = params[-10:]
        event_date_new = params[-21:-11]
        id = params[:-22]
        if not event_id_hit(id):
            bot.send_message(chat_id=update.message.chat_id,
                             text="No existe ningún evento con el identificador " + id)
            logging.warning("Se ha intentado modificar un evento con un identificador no válido a petición del cliente ID " + str(
            update.message.chat_id))
            return False
        logging.debug("Identificador de evento encontrado: " + id)
        if len(event_date_new) != 10:
            bot.send_message(chat_id=update.message.chat_id,
                             text="La nueva fecha de evento debe ir en formato DD.MM.AAAA")
            logging.warning("Se ha introducido mal la nueva fecha de evento al intentar modificar un evento a petición del cliente ID " + str(
            update.message.chat_id))
            return False
        if len(event_date_new.split(".")) != 3:
            bot.send_message(chat_id=update.message.chat_id,
                             text="La nueva fecha de evento debe ir en formato DD.MM.AAAA")
            logging.warning("Se ha introducido mal la nueva fecha de evento al intentar modificar un evento a petición del cliente ID " + str(
            update.message.chat_id))
            return False
        if len(reminder_date_new) != 10:
            bot.send_message(chat_id=update.message.chat_id,
                             text="La nueva fecha de recordatorio debe ir en formato DD.MM.AAAA")
            logging.warning("Se ha introducido mal la nueva fecha de recordatorio al intentar modificar un evento a petición del cliente ID " + str(
            update.message.chat_id))
            return False
        if len(reminder_date_new.split(".")) != 3:
            bot.send_message(chat_id=update.message.chat_id,
                             text="La nueva fecha de recordatorio debe ir en formato DD.MM.AAAA")
            logging.warning("Se ha introducido mal la nueva fecha de recordatorio al intentar modificar un evento a petición del cliente ID " + str(
            update.message.chat_id))
            return False
        logging.debug("Modificando el evento con ID " + id)
        script_path = os.path.dirname(sys.argv[0])
        with open(script_path + events_file, 'r') as f1:
            events = json.load(f1)
        events_new = {}
        events_new['events'] = []
        for event in events['events']:
            event_id = event['id']
            title = event['title']
            if int(id) != event_id:
                event_date = event['event_date']
                reminder_date = event['reminder_date']
            else:
                event_date = event_date_new
                reminder_date = reminder_date_new
            events_new['events'].append({
                'event_id': event_id,
                'title': title,
                'event_date': event_date,
                'reminder_date': reminder_date
            })
        with open(script_path + events_tmp_file, 'w+') as f2:
            json.dump(events_new, f2, indent=2)
        copyfile(script_path + events_tmp_file, script_path + events_file)
        os.remove(script_path + events_tmp_file)
        bot.send_message(chat_id=update.message.chat_id,
                         text="Se ha modificado el evento con el ID " + str(id))
        logging.info(
            "Alfred modificó el evento con el ID " + str(id) + " a petición del client ID " + str(
                update.message.chat_id))
        return True


# Función opción /events_remove
def events_remove(bot, update):
    if client_authentication(bot, update.message.chat_id):
        event_id = update.message.text.replace("/events_remove ", "")
        if event_id == "/events_remove":
            bot.send_message(chat_id=update.message.chat_id,
                             text="Para eliminar un evento debe proceder como se indica:\n"
                                  "  /events_remove <ID>")
            return False
        logging.debug("Comprobando identificador de evento antes de borrarlo")
        if not event_id_hit(event_id):
            bot.send_message(chat_id=update.message.chat_id,
                             text="No existe ningún evento con el identificador " + event_id)
            logging.warning("Se ha intentado borrar un evento con un identificador no válido a petición del client ID " + str(
                update.message.chat_id))
            return False
        logging.debug("Identificador de evento encontrado: " + event_id)
        logging.debug("Borrando el evento con ID " + event_id)
        script_path = os.path.dirname(sys.argv[0])
        with open(script_path + events_file, 'r') as f1:
            events = json.load(f1)
        events_new = {}
        events_new['events'] = []
        for event in events['events']:
            if int(event_id) != event['id']:
                id = event['id']
                title = event['title']
                event_date = event['event_date']
                reminder_date = event['reminder_date']
                events_new['events'].append({
                    'id': id,
                    'title': title,
                    'event_date': event_date,
                    'reminder_date': reminder_date
                })
        with open(script_path + events_tmp_file, 'w+') as f2:
            json.dump(events_new, f2, indent=2)
        copyfile(script_path + events_tmp_file, script_path + events_file)
        os.remove(script_path + events_tmp_file)
        bot.send_message(chat_id=update.message.chat_id,
                         text="Se ha eliminado el evento con el ID " + event_id)
        logging.info("Alfred eliminó el evento el ID " + event_id + " a petición del client ID " + str(
            update.message.chat_id))
        if events_sort():
            bot.send_message(chat_id=update.message.chat_id, text="Se ha reordenado la lista de eventos")
            logging.info("Lista de eventos reordenada")
        return True


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
    log_file = config['DEFAULT']['ALFRED_LOG_FILE']
    log_level = config['DEFAULT']['ALFRED_LOG_LEVEL']
    bot_token = config['DEFAULT']['BOT_TOKEN']
    global client_ids
    client_ids = config['DEFAULT']['CLIENT_IDS']
    global events_file
    events_file = config['DEFAULT']['EVENTS_DB_FILE']
    global events_tmp_file
    events_tmp_file = config['DEFAULT']['EVENTS_DB_TMP_FILE']

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
