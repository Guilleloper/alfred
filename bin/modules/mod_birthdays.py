#########################################################
# ENVIO DE MENSAJES VIA ALFRED PARA RECORDAR CUMPLEAÑOS #
#########################################################


# CARGA DE LIBRERÍAS

import logging
import json
import sys
import os
import datetime
import time
import telegram
from shutil import copyfile


# DEFINICIÓN DE FUNCIONES

# Función para ordenar el fichero de cumpleaños, por dia y mes.
def sort(bot, update):

    # Carga de fichero de configuración
    script_path = os.path.dirname(sys.argv[0])
    with open(script_path + '/../config/config.json', 'r') as f:
        config = json.load(f)
    db_file = config['BIRTHDAYS']['DB_FILE']
    db_tmp_file = config['BIRTHDAYS']['TMP_PATH'] + "/birthdays.tmp"

    # Creacion de nueva lista de items, transformando los valores de la clave "date" a timestamp
    # (teniendo solo en cuenta el dia y el mes)
    with open(db_file, 'r') as f1:
        items = json.load(f1)
    items_new = {}
    items_new['birthdays'] = []
    for item in items['birthdays']:
        item_id = item['id']
        item_name = item['name']
        item_date = item['date']
        item_date_year = "2000"
        item_date_month = item_date.split(".")[1]
        item_date_day = item_date.split(".")[0]
        item_date_new = item_date_day + "." + item_date_month + "." + item_date_year
        item_date_new_tstmp = time.mktime(datetime.datetime.strptime(item_date_new, "%d.%m.%Y").timetuple())
        items_new['birthdays'].append({
            'id': item_id,
            'name': item_name,
            'date': item_date_new_tstmp
        })

    # Ordenar el fichero de cumpleaños a partir de la clave "date"
    items_new_sorted = sorted(items_new['birthdays'], key=lambda k: k['date'])
    items_new = {}
    items_new['birthdays'] = []
    item_id_new = 1
    for item in items_new_sorted:
        for item_ori in items['birthdays']:
            if item['id'] == item_ori['id']:
                item_name = item_ori['name']
                item_date = item_ori['date']
        items_new['birthdays'].append({
            'id': item_id_new,
            'name': item_name,
            'date': item_date
        })
        item_id_new += 1

    # Comprobar si ha habido cambios en la ordenacion de las tareas y reordenar si aplica
    if items != items_new:
        with open(db_tmp_file, 'w+') as f2:
            json.dump(items_new, f2, indent=2)
        copyfile(db_tmp_file, db_file)
        os.remove(db_tmp_file)
        bot.send_message(chat_id=update.message.chat_id, text="Se ha reordenado la lista de cumpleaños")
        logging.info("Lista de cumpleaños reordenada")
        return True
    else:
        return False


# Función para comprobar si existe un evento con un ID determinado
def id_hit(item_id):

    # Carga de fichero de configuración
    script_path = os.path.dirname(sys.argv[0])
    with open(script_path + '/../config/config.json', 'r') as f:
        config = json.load(f)
    db_file = config['BIRTHDAYS']['DB_FILE']

    # Comprobacion de existencia del ID
    with open(db_file, 'r') as f1:
        items = json.load(f1)
    for item in items['birthdays']:
        if int(item_id) == item['id']:
            return True
    return False


# Función para mostrar los cumpleaños
def list(bot, update):

    # Carga de fichero de configuración
    script_path = os.path.dirname(sys.argv[0])
    with open(script_path + '/../config/config.json', 'r') as f:
        config = json.load(f)
    db_file = config['BIRTHDAYS']['DB_FILE']
    with open(db_file, 'r') as f:
        items = json.load(f)
    if items['birthdays'] == []:
        bot.send_message(chat_id=update.message.chat_id, text="Cumpleaños actuales:\n"
                                                              "(vacío)")
    else:
        bot.send_message(chat_id=update.message.chat_id, text="Cumpleaños actuales:\n")
        for item in items['birthdays']:
            item_id = item['id']
            item_name = item['name']
            item_date = item['date']
            bot.send_message(chat_id=update.message.chat_id, text="  ID: " + str(item_id) + "\n"
                                                                  "  Nombre: " + item_name + "\n"
                                                                  "  Fecha: " + item_date + "\n")


# Función para añadir un evento
def add(bot, update):

    # Carga de fichero de configuración
    script_path = os.path.dirname(sys.argv[0])
    with open(script_path + '/../config/config.json', 'r') as f:
        config = json.load(f)
    db_file = config['BIRTHDAYS']['DB_FILE']
    db_tmp_file = config['BIRTHDAYS']['TMP_PATH'] + "/events.tmp"

    # Comprobaciones previas
    logging.debug("Realizando comprobaciones previas antes de crear un cumpleaños")
    params = update.message.text.replace("/birthdays_add ", "")
    if params == "/birthdays_add":
        bot.send_message(chat_id=update.message.chat_id,
                         text="Para añadir un cumpleaños debe proceder como se indica:\n"
                              "  /birthdays_add <nombre> <fecha de nacimiento>\n"
                              "  (la fecha en formato DD.MM.AAAA)")
        return False
    if len(params.split(" ")) < 2:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Sintanxis incorrecta. Para añadir un cumpleaños debe proceder como se indica:\n"
                              "  /birthdays_add <nombre> <fecha de nacimiento>\n"
                              "  (la fecha en formato DD.MM.AAAA)")
        logging.warning("Sintaxis incorrecta al intentar crear un cumpleaños a petición del cliente ID " + str(
            update.message.chat_id))
        return False
    date_new = params[-10:]
    name_new = params[:-11]
    if len(date_new) != 10:
        bot.send_message(chat_id=update.message.chat_id,
                         text="La fecha de nacimiento debe ir en formato DD.MM.AAAA")
        logging.warning(
            "Se ha introducido mal la fecha de nacimiento al intentar crear un cumpleaños a petición del cliente ID " + str(
                update.message.chat_id))
        return False
    if len(date_new.split(".")) != 3:
        bot.send_message(chat_id=update.message.chat_id,
                         text="La fecha de nacimiento debe ir en formato DD.MM.AAAA")
        logging.warning(
            "Se ha introducido mal la fecha de nacimiento al intentar crear un cumpleaños a petición del cliente ID " + str(
                update.message.chat_id))
        return False

    # Creacion del nuevo cumpleaños
    logging.debug("Creando un nuevo cumpleaños")
    with open(db_file, 'r') as f1:
        items = json.load(f1)
    items_new = {}
    items_new['birthdays'] = []
    item_id = 0
    for item in items['birthdays']:
        item_id = item['id']
        item_name = item['name']
        item_date = item['date']
        items_new['birthdays'].append({
            'id': item_id,
            'name': item_name,
            'date': item_date
        })
    id_new = item_id + 1
    items_new['birthdays'].append({
        'id': id_new,
        'name': name_new,
        'date': date_new
    })
    with open(db_tmp_file, 'w+') as f2:
        json.dump(items_new, f2, indent=2)
    copyfile(db_tmp_file, db_file)
    os.remove(db_tmp_file)
    bot.send_message(chat_id=update.message.chat_id,
                     text="Se ha creado el cumpleaños de " + name_new + " con el ID " + str(id_new))
    logging.info(
        "Alfred creó el cumpleaños " + name_new + " con el ID " + str(id_new) + " a petición del client ID " + str(
            update.message.chat_id))
    return True


# Función para eliminar un cumpleaños
def remove(bot, update):

    # Carga de fichero de configuracion
    script_path = os.path.dirname(sys.argv[0])
    with open(script_path + '/../config/config.json', 'r') as f:
        config = json.load(f)
    db_file = config['BIRTHDAYS']['DB_FILE']
    db_tmp_file = config['BIRTHDAYS']['TMP_PATH'] + "/events.tmp"

    # Comprobaciones previas
    id = update.message.text.replace("/birthdays_remove ", "")
    if id == "/birthdays_remove":
        bot.send_message(chat_id=update.message.chat_id,
                         text="Para eliminar un cumpleaños debe proceder como se indica:\n"
                              "  /birthdays_remove <ID>")
        return False
    logging.debug("Comprobando identificador de cumpleaños antes de borrarlo")
    if not id_hit(id):
        bot.send_message(chat_id=update.message.chat_id,
                         text="No existe ningún cumpleaños con el identificador " + id)
        logging.warning("Se ha intentado borrar un cumpleaños con un identificador no válido a petición del client ID " + str(
            update.message.chat_id))
        return False
    logging.debug("Identificador de cumpleaños encontrado: " + id)

    # Borrado del cumpleaños
    logging.debug("Borrando el cumpleaños con ID " + id)
    with open(db_file, 'r') as f1:
        items = json.load(f1)
    items_new = {}
    items_new['birthdays'] = []
    for item in items['birthdays']:
        if int(id) != item['id']:
            item_id = item['id']
            item_name = item['name']
            item_date = item['date']
            items_new['birthdays'].append({
                'id': item_id,
                'name': item_name,
                'date': item_date
            })
    with open(db_tmp_file, 'w+') as f2:
        json.dump(items_new, f2, indent=2)
    copyfile(db_tmp_file, db_file)
    os.remove(db_tmp_file)
    bot.send_message(chat_id=update.message.chat_id,
                     text="Se ha eliminado el cumpleaños con el ID " + id)
    logging.info("Alfred eliminó el cumpleaños con el ID " + id + " a petición del client ID " + str(
        update.message.chat_id))
    return True


# PROGRAMA PRINCIPAL

def main():

    # Carga de fichero de configuración:
    script_path = os.path.dirname(sys.argv[0])
    with open(script_path + '/../../config/config.json', 'r') as f:
        config = json.load(f)
    bot_token = config['DEFAULT']['BOT_TOKEN']
    client_ids = config['DEFAULT']['CLIENT_IDS']
    log_level = config['BIRTHDAYS']['LOG_LEVEL']
    log_to_file = config['BIRTHDAYS']['ADDITIONAL_LOG_TO_FILE']
    log_file = config['BIRTHDAYS']['LOG_FILE']
    db_file = config['BIRTHDAYS']['DB_FILE']

    # Configurar logger a stdout
    logging.basicConfig(level=getattr(logging, log_level),
                        format="[%(asctime)s] [%(levelname)s] - [Birthdays] - %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S")

    # Configurar adcionalmente logger a fichero
    if log_to_file:
        log_handler = logging.FileHandler(log_file, 'a')
        log_handler.setLevel(getattr(logging, log_level))
        log_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] - [Birthdays] - %(message)s", "%Y-%m-%d %H:%M:%S"))
        logging.getLogger('').addHandler(log_handler)

    # Inicio
    logging.info("Inicio del programa")

    # Crear una instancia del bot
    bot = telegram.Bot(token=bot_token)

    # Obtener fecha actual
    actual_date = datetime.datetime.now()
    actual_year = int(actual_date.year)
    actual_month = int(actual_date.month)
    actual_day = int(actual_date.day)

    # Comprobar uno por uno los eventos y enviar recordatorio si aplica
    hits = 0
    with open(db_file, 'r') as f:
        f_json = json.load(f)
    for item in f_json['birthdays']:
        item_name = item['name']
        item_date = item['date']

        # Comprobacion de si se cumple la condicion para enviar recordatorio
        item_month = int(item_date.split(".")[1])
        item_day = int(item_date.split(".")[0])
        if actual_month == item_month and actual_day == item_day:
            # Calculo de la edad
            item_year = int(item_date.split(".")[2])
            years = actual_year - item_year

            # Envio del mensaje
            for client_id in client_ids:
                bot.send_message(chat_id=client_id, text="Recordatorio de cumpleaños:\n"
                                 "  Cumpleaños de " + item_name + "\n"
                                 "  (" + str(years) + " años)")
            hits += 1

    # Comprobar numero de hits
    if hits > 0:
        logging.info("Se han enviado " + str(hits) + " recordatorios")
    else:
        logging.info("No se ha enviado ningún recordatorio")

    # Fin
    logging.info("Fin del programa")


if __name__ == '__main__':
    main()
