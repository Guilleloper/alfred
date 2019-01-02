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

# PROGRAMA PRINCIPAL

def main():

    # Carga de fichero de configuración:
    script_path = os.path.dirname(sys.argv[0])
    with open(script_path + '/../config/config.json', 'r') as f:
        config = json.load(f)
    log_file = config['DEFAULT']['EVENTS_LOG_FILE']
    log_level = config['DEFAULT']['EVENTS_LOG_LEVEL']
    events_file = config['DEFAULT']['EVENTS_DB_FILE']
    bot_token = config['DEFAULT']['BOT_TOKEN']
    client_ids = config['DEFAULT']['CLIENT_IDS']

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
    with open(script_path + events_file, 'r') as f:
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
