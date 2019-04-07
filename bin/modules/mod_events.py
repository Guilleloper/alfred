#######################################################
# ENVIO DE MENSAJES VIA ALFRED PARA RECORDAR EVENTOS #
######################################################


# CARGA DE LIBRERÍAS

import logging
import json
import sys
import os
import time
import datetime
import telegram
from shutil import copyfile


# DEFINICION DE FUNCIONES

# Funcion para ordenar el fichero de eventos, por fecha del evento.
def sort(bot, update):

    # Carga de fichero de configuracion:
    script_path = os.path.dirname(sys.argv[0])
    with open(script_path + '/../config/config.json', 'r') as f:
        config = json.load(f)
    db_file = config['EVENTS']['DB_FILE']
    db_tmp_file = config['EVENTS']['TMP_PATH'] + "/events.tmp"

    # Creacion de nueva lista de items, transformando los valores de la clave "date" a timestamp
    with open(db_file, 'r') as f1:
        items = json.load(f1)
    items_new = {}
    items_new['events'] = []
    for item in items['events']:
        item_id = item['id']
        item_title = item['title']
        item_event_date = item['event_date']
        item_reminder_date = item['reminder_date']
        item_date_new_tstmp = time.mktime(datetime.datetime.strptime(item_event_date, "%d.%m.%Y").timetuple())
        items_new['events'].append({
            'id': item_id,
            'title': item_title,
            'event_date': item_date_new_tstmp,
            'reminder_date': item_reminder_date
        })

    # Ordenar el fichero de eventos a partir de la clave "event_date"
    items_new_sorted = sorted(items_new['events'], key=lambda k: k['event_date'])
    items_new = {}
    items_new['events'] = []
    item_id_new = 1
    for item in items_new_sorted:
        for item_ori in items['events']:
            if item['id'] == item_ori['id']:
                item_title = item_ori['title']
                item_event_date = item_ori['event_date']
                item_reminder_date = item_ori['reminder_date']
        items_new['events'].append({
            'id': item_id_new,
            'title': item_title,
            'event_date': item_event_date,
            'reminder_date': item_reminder_date
        })
        item_id_new += 1

    # Comprobar si ha habido cambios en la ordenacion de las tareas y reordenar si aplica
    if items != items_new:
        with open(db_tmp_file, 'w+') as f2:
            json.dump(items_new, f2, indent=2)
        copyfile(db_tmp_file, db_file)
        os.remove(db_tmp_file)
        bot.send_message(chat_id=update.message.chat_id, text="Se ha reordenado la lista de eventos")
        logging.info("Lista de eventos reordenada")
        return True
    else:
        return False


# Función para comprobar si existe un evento con un ID determinado
def id_hit(item_id):

    # Carga de fichero de configuración
    script_path = os.path.dirname(sys.argv[0])
    with open(script_path + '/../config/config.json', 'r') as f:
        config = json.load(f)
    db_file = config['EVENTS']['DB_FILE']

    # Comprobacion de existencia del ID
    with open(db_file, 'r') as f1:
        items = json.load(f1)
    for item in items['events']:
        if int(item_id) == item['id']:
            return True
    return False


# Función para mostrar los eventos
def list(bot, update):

    # Carga de fichero de configuración
    script_path = os.path.dirname(sys.argv[0])
    with open(script_path + '/../config/config.json', 'r') as f:
        config = json.load(f)
    db_file = config['EVENTS']['DB_FILE']

    # Listado de eventos
    with open(db_file, 'r') as f:
        items = json.load(f)
    if items == "":
        bot.send_message(chat_id=update.message.chat_id, text="Eventos actuales:\n"
                                                              "(vacío)")
    else:
        bot.send_message(chat_id=update.message.chat_id, text="Eventos actuales:\n")
        for item in items['events']:
            item_id = item['id']
            item_title = item['title']
            item_event_date = item['event_date']
            item_reminder_date = item['reminder_date']
            bot.send_message(chat_id=update.message.chat_id, text="  ID: " + str(item_id) + "\n"
                                                                  "  Evento: " + item_title + "\n"
                                                                  "  Fecha: " + item_event_date + "\n"
                                                                  "  Avisar a partir de: " + item_reminder_date + "\n")


# Función para añadir un evento
def add(bot, update):

    # Carga de fichero de configuración
    script_path = os.path.dirname(sys.argv[0])
    with open(script_path + '/../config/config.json', 'r') as f:
        config = json.load(f)
    db_file = config['EVENTS']['DB_FILE']
    db_tmp_file = config['EVENTS']['TMP_PATH'] + "/events.tmp"

    # Comprobaciones previas
    logging.debug("Realizando comprobaciones previas antes de crear un evento")
    params = update.message.text.replace("/events_add ", "")
    if params == "/events_add":
        bot.send_message(chat_id=update.message.chat_id,
                         text="Para añadir un evento debe proceder como se indica:\n"
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
        logging.warning(
            "Se ha introducido mal la fecha de evento al intentar crear un evento a petición del cliente ID " + str(
                update.message.chat_id))
        return False
    if len(event_date_new.split(".")) != 3:
        bot.send_message(chat_id=update.message.chat_id,
                         text="La fecha de evento debe ir en formato DD.MM.AAAA")
        logging.warning(
            "Se ha introducido mal la fecha de evento al intentar crear un evento a petición del cliente ID " + str(
                update.message.chat_id))
        return False
    if len(reminder_date_new) != 10:
        bot.send_message(chat_id=update.message.chat_id,
                         text="La fecha de recordatorio debe ir en formato DD.MM.AAAA")
        logging.warning(
            "Se ha introducido mal la fecha de recordatorio al intentar crear un evento a petición del cliente ID " + str(
                update.message.chat_id))
        return False
    if len(reminder_date_new.split(".")) != 3:
        bot.send_message(chat_id=update.message.chat_id,
                         text="La fecha de recordatorio debe ir en formato DD.MM.AAAA")
        logging.warning(
            "Se ha introducido mal la fecha de recordatorio al intentar crear un evento a petición del cliente ID " + str(
                update.message.chat_id))
        return False

    # Creacion de nuevo evento
    logging.debug("Creando un nuevo evento")
    with open(db_file, 'r') as f1:
        items = json.load(f1)
    items_new = {}
    items_new['events'] = []
    item_id = 0
    for item in items['events']:
        item_id = item['id']
        item_title = item['title']
        item_event_date = item['event_date']
        item_reminder_date = item['reminder_date']
        items_new['events'].append({
            'id': item_id,
            'title': item_title,
            'event_date': item_event_date,
            'reminder_date': item_reminder_date
        })
    id_new = item_id + 1
    items_new['events'].append({
        'id': id_new,
        'title': title_new,
        'event_date': event_date_new,
        'reminder_date': reminder_date_new
    })
    with open(db_tmp_file, 'w+') as f2:
        json.dump(items_new, f2, indent=2)
    copyfile(db_tmp_file, db_file)
    os.remove(db_tmp_file)
    bot.send_message(chat_id=update.message.chat_id,
                     text="Se ha creado el evento " + title_new + " con el ID " + str(id_new))
    logging.info(
        "Alfred creó el evento " + title_new + " con el ID " + str(id_new) + " a petición del client ID " + str(
            update.message.chat_id))
    return True


# Funcion para editar un evento
def edit(bot, update):

    # Carga de fichero de configuracion
    script_path = os.path.dirname(sys.argv[0])
    with open(script_path + '/../config/config.json', 'r') as f:
        config = json.load(f)
    db_file = config['EVENTS']['DB_FILE']
    db_tmp_file = config['EVENTS']['TMP_PATH'] + "/events.tmp"

    # Comprobaciones previas
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
    if not id_hit(id):
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

    # Modificacion del evento
    logging.debug("Modificando el evento con ID " + id)
    with open(db_file, 'r') as f1:
        items = json.load(f1)
    items_new = {}
    items_new['events'] = []
    for item in items['events']:
        item_id = item['id']
        item_title = item['title']
        if int(id) != item_id:
            item_event_date = item['event_date']
            item_reminder_date = item['reminder_date']
        else:
            item_event_date = event_date_new
            item_reminder_date = reminder_date_new
        items_new['events'].append({
            'id': item_id,
            'title': item_title,
            'event_date': item_event_date,
            'reminder_date': item_reminder_date
        })
    with open(db_tmp_file, 'w+') as f2:
        json.dump(items_new, f2, indent=2)
    copyfile(db_tmp_file, db_file)
    os.remove(db_tmp_file)
    bot.send_message(chat_id=update.message.chat_id,
                     text="Se ha modificado el evento con el ID " + str(id))
    logging.info(
        "Alfred modificó el evento con el ID " + str(id) + " a petición del client ID " + str(
            update.message.chat_id))
    return True


def remove(bot, update):

    # Carga de fichero de configuracion
    script_path = os.path.dirname(sys.argv[0])
    with open(script_path + '/../config/config.json', 'r') as f:
        config = json.load(f)
    db_file = config['EVENTS']['DB_FILE']
    db_tmp_file = config['EVENTS']['TMP_PATH'] + "/events.tmp"

    # Comprobaciones previas
    id = update.message.text.replace("/events_remove ", "")
    if id == "/events_remove":
        bot.send_message(chat_id=update.message.chat_id,
                         text="Para eliminar un evento debe proceder como se indica:\n"
                              "  /events_remove <ID>")
        return False
    logging.debug("Comprobando identificador de evento antes de borrarlo")
    if not id_hit(id):
        bot.send_message(chat_id=update.message.chat_id,
                         text="No existe ningún evento con el identificador " + id)
        logging.warning("Se ha intentado borrar un evento con un identificador no válido a petición del client ID " + str(
            update.message.chat_id))
        return False
    logging.debug("Identificador de evento encontrado: " + id)

    # Borrado del evento
    logging.debug("Borrando el evento con ID " + id)
    with open(db_file, 'r') as f1:
        items = json.load(f1)
    items_new = {}
    items_new['events'] = []
    for item in items['events']:
        if int(id) != item['id']:
            item_id = item['id']
            item_title = item['title']
            item_event_date = item['event_date']
            item_reminder_date = item['reminder_date']
            items_new['events'].append({
                'id': item_id,
                'title': item_title,
                'event_date': item_event_date,
                'reminder_date': item_reminder_date
            })
    with open(db_tmp_file, 'w+') as f2:
        json.dump(items_new, f2, indent=2)
    copyfile(db_tmp_file, db_file)
    os.remove(db_tmp_file)
    bot.send_message(chat_id=update.message.chat_id,
                     text="Se ha eliminado el evento con el ID " + id)
    logging.info("Alfred eliminó el evento con el ID " + id + " a petición del client ID " + str(
        update.message.chat_id))
    return True


# PROGRAMA PRINCIPAL

def main():

    # Carga de fichero de configuracion:
    script_path = os.path.dirname(sys.argv[0])
    with open(script_path + '/../../config/config.json', 'r') as f:
        config = json.load(f)
    bot_token = config['DEFAULT']['BOT_TOKEN']
    client_ids = config['DEFAULT']['CLIENT_IDS']
    log_file = config['EVENTS']['LOG_FILE']
    log_level = config['EVENTS']['LOG_LEVEL']
    db_file = config['EVENTS']['DB_FILE']

    # Configurar logger a fichero:
    logging.basicConfig(level=getattr(logging, log_level),
                        format="[%(asctime)s] [%(levelname)s] - [Events] - %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                        filename=log_file,
                        filemode='a')

    # Configurar logger a stdout:
    console = logging.StreamHandler()
    console.setLevel(getattr(logging, log_level))
    console.setFormatter(logging.Formatter("[%(levelname)s] - [Events] - %(message)s"))
    logging.getLogger('').addHandler(console)

    # Inicio
    logging.info("Inicio del programa")

    # Crear una instancia del bot
    bot = telegram.Bot(token=bot_token)

    # Obtener fecha actual
    actual_date_tstmp = time.time()

    # Comprobar uno por uno los enventos y enviar recordatorio si aplica
    event_hits = 0
    with open(db_file, 'r') as f:
        events = json.load(f)
    for event in events['events']:
        title = event['title']
        event_date = event['event_date']
        reminder_date = event['reminder_date']
        # Comprobacion de si se cumple la condicion para enviar recordatorio
        reminder_date_tstmp = time.mktime(datetime.datetime.strptime(reminder_date, "%d.%m.%Y").timetuple())
        if actual_date_tstmp >= reminder_date_tstmp:
            # Envio del mensaje
            for client_id in client_ids:
                bot.send_message(chat_id=client_id, text="Recordatorio de evento:\n"
                                 "  Evento:  " + title + "\n"
                                 "  Fecha: " + event_date)
            event_hits += 1

    # Comprobar numero de hits
    if event_hits > 0:
        logging.info("Se han enviado " + str(event_hits) + " recordatorios")
    else:
        logging.info("No se ha enviado ningún recordatorio")

    # Fin
    logging.info("Fin del programa")


if __name__ == '__main__':
    main()
