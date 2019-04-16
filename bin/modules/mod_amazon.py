####################################
# GESTIÓN DE PRODUCTOS DE AMAZON   #
#                                  #
# - SEGUIMIENTO DE PRODUCTOS       #
# - CONSULTA Y GUARDADO DE PRECIOS #
# - ANALISIS DE OFERTAS            #
# - ENVÍO DE NOTIFICACIONES        #
####################################


# CARGA DE LIBRERÍAS

import logging
import json
import sys
import os
import time
import datetime
import telegram
from shutil import copyfile
import random
from bs4 import BeautifulSoup
import requests
import graphyte


# DEFINICION DE FUNCIONES

# Funcion para ordenar el fichero de productos, por fecha del inicio del seguimiento.
def sort(bot, update):

    # Carga de fichero de configuracion:
    script_path = os.path.dirname(sys.argv[0])
    with open(script_path + '/../config/config.json', 'r') as f:
        config = json.load(f)
    db_file = config['AMAZON']['DB_FILE']
    db_tmp_file = config['AMAZON']['TMP_PATH'] + "/amazon.tmp"

    # Creacion de nueva lista de items, transformando los valores de la clave "initial_date" a timestamp
    with open(db_file, 'r') as f1:
        items = json.load(f1)
    items_new = {}
    items_new['amazon'] = []
    for item in items['amazon']:
        item_id = item['id']
        item_name = item['name']
        item_initial_date = item['initial_date']
        item_url = item['url']
        item_initial_date_tstmp = time.mktime(datetime.datetime.strptime(item_initial_date, "%d.%m.%Y").timetuple())
        items_new['amazon'].append({
            'id': item_id,
            'name': item_name,
            'initial_date': item_initial_date_tstmp,
            'url': item_url
        })

    # Ordenar el fichero de productos a partir de la clave "initial_date"
    items_new_sorted = sorted(items_new['amazon'], key=lambda k: k['initial_date'])
    items_new = {}
    items_new['amazon'] = []
    item_id_new = 1
    for item in items_new_sorted:
        for item_ori in items['amazon']:
            if item['id'] == item_ori['id']:
                item_name = item_ori['name']
                item_initial_date = item_ori['initial_date']
                item_url = item_ori['url']
        items_new['amazon'].append({
            'id': item_id_new,
            'name': item_name,
            'initial_date': item_initial_date,
            'url': item_url
        })
        item_id_new += 1

    # Comprobar si ha habido cambios en la ordenacion de los productos y reordenar si aplica
    if items != items_new:
        with open(db_tmp_file, 'w+') as f2:
            json.dump(items_new, f2, indent=2)
        copyfile(db_tmp_file, db_file)
        os.remove(db_tmp_file)
        bot.send_message(chat_id=update.message.chat_id, text="Se ha reordenado la lista de productos")
        logging.info("Lista de productos reordenada")
        return True
    else:
        return False


# Función para comprobar si existe un producto en seguimiento con un ID determinado
def id_hit(item_id):

    # Carga de fichero de configuración
    script_path = os.path.dirname(sys.argv[0])
    with open(script_path + '/../config/config.json', 'r') as f:
        config = json.load(f)
    db_file = config['AMAZON']['DB_FILE']

    # Comprobacion de existencia del ID
    with open(db_file, 'r') as f1:
        items = json.load(f1)
    for item in items['amazon']:
        if int(item_id) == item['id']:
            return True
    return False


# Función para mostrar los productos en seguimiento
def list(bot, update):

    # Carga de fichero de configuración
    script_path = os.path.dirname(sys.argv[0])
    with open(script_path + '/../config/config.json', 'r') as f:
        config = json.load(f)
    db_file = config['AMAZON']['DB_FILE']

    # Listado de productos en seguimiento
    with open(db_file, 'r') as f:
        items = json.load(f)
    if items['amazon'] == []:
        bot.send_message(chat_id=update.message.chat_id, text="Productos en seguimiento:\n"
                                                              "(vacío)")
    else:
        bot.send_message(chat_id=update.message.chat_id, text="Productos en seguimiento:\n")
        for item in items['amazon']:
            item_id = item['id']
            item_name = item['name']
            item_initial_date = item['initial_date']
            item_url = item['url']
            bot.send_message(chat_id=update.message.chat_id, text="  ID: " + str(item_id) + "\n"
                                                                  "  Nombre: " + item_name + "\n"
                                                                  "  En seguimiento desde: " + item_initial_date + "\n"
                                                                  "  URL: " + item_url + "\n")


# Función para poner un producto en seguimiento
def add(bot, update):

    # Carga de fichero de configuración
    script_path = os.path.dirname(sys.argv[0])
    with open(script_path + '/../config/config.json', 'r') as f:
        config = json.load(f)
    db_file = config['AMAZON']['DB_FILE']
    db_tmp_file = config['AMAZON']['TMP_PATH'] + "/amazon.tmp"

    # Comprobaciones previas
    logging.debug("Realizando comprobaciones previas antes de poner un producto en seguimiento")
    params = update.message.text.replace("/amazon_add ", "")
    if params == "/amazon_add":
        bot.send_message(chat_id=update.message.chat_id,
                         text="Para poner en seguimiento un producto debe proceder como se indica:\n"
                              "  /amazon_add <nombre> <url>\n")
        return False
    if len(params.split(" ")) < 2:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Sintanxis incorrecta. Para poner en seguimiento un producto debe proceder como se indica:\n"
                              "  /amazon_add <nombre> <url>\n")
        logging.warning("Sintaxis incorrecta al intentar poner en seguimiento un producto a petición del cliente ID " + str(
            update.message.chat_id))
        return False
    name_new = params.split(" ")[0:-1]
    name_new = " ".join(name_new)
    print(name_new)
    print(type(name_new))
    url_new = params.split(" ")[-1]
    if url_new.startswith("https://www.amazon.es/") is False:
        bot.send_message(chat_id=update.message.chat_id,
                         text="La url introducida no es correcta. Esta ha de ser del tipo \"https://www.amazon.es/...\"")
        logging.warning(
            "Se ha introducido una url incorrecta al intentar poner en seguimiento un producto a petición del cliente ID " + str(
                update.message.chat_id))
        return False
    start = 'dp/'
    end = '/'
    url_new = url_new[url_new.find(start)+len(start):url_new.rfind(end)]
    url_new = "https://www.amazon.es/dp/" + url_new
    initial_date_new = time.strftime("%d.%m.%Y")

    # Poner producto en seguimiento:
    logging.debug("Poniendo un producto en seguimiento")
    with open(db_file, 'r') as f1:
        items = json.load(f1)
    items_new = {}
    items_new['amazon'] = []
    item_id = 0
    for item in items['amazon']:
        item_id = item['id']
        item_name = item['name']
        item_initial_date = item['initial_date']
        item_url = item['url']
        items_new['amazon'].append({
            'id': item_id,
            'name': item_name,
            'initial_date': item_initial_date,
            'url': item_url
        })
    id_new = item_id + 1
    items_new['amazon'].append({
        'id': id_new,
        'name': name_new,
        'initial_date': initial_date_new,
        'url': url_new
    })
    with open(db_tmp_file, 'w+') as f2:
        json.dump(items_new, f2, indent=2)
    copyfile(db_tmp_file, db_file)
    os.remove(db_tmp_file)
    bot.send_message(chat_id=update.message.chat_id,
                     text="Se ha puesto en seguimiento el producto " + name_new + " con el ID " + str(id_new))
    logging.info(
        "Alfred puso en seguimiento el producto " + name_new + " con el ID " + str(id_new) + " a petición del client ID " + str(
            update.message.chat_id))
    return True


# Funcion para eliminar un producto en seguimiento
def remove(bot, update):

    # Carga de fichero de configuracion
    script_path = os.path.dirname(sys.argv[0])
    with open(script_path + '/../config/config.json', 'r') as f:
        config = json.load(f)
    db_file = config['AMAZON']['DB_FILE']
    db_tmp_file = config['AMAZON']['TMP_PATH'] + "/amazon.tmp"

    # Comprobaciones previas
    id = update.message.text.replace("/amazon_remove ", "")
    if id == "/amazon_remove":
        bot.send_message(chat_id=update.message.chat_id,
                         text="Para eliminar un producto en seguimiento debe proceder como se indica:\n"
                              "  /amazon_remove <ID>")
        return False
    logging.debug("Comprobando identificador de producto en seguimiento antes de borrarlo")
    if not id_hit(id):
        bot.send_message(chat_id=update.message.chat_id,
                         text="No existe ningún producto en seguimiento con el identificador " + id)
        logging.warning("Se ha intentado borrar un producto en seguimiento con un identificador no válido a petición del client ID " + str(
            update.message.chat_id))
        return False
    logging.debug("Identificador de producto en seguimiento encontrado: " + id)

    # Borrado del evento
    logging.debug("Borrando el producto en seguimiento con ID " + id)
    with open(db_file, 'r') as f1:
        items = json.load(f1)
    items_new = {}
    items_new['amazon'] = []
    for item in items['amazon']:
        if int(id) != item['id']:
            item_id = item['id']
            item_name = item['name']
            item_initial_date = item['initial_date']
            item_url = item['url']
            items_new['amazon'].append({
                'id': item_id,
                'name': item_name,
                'initial_date': item_initial_date,
                'url': item_url
            })
    with open(db_tmp_file, 'w+') as f2:
        json.dump(items_new, f2, indent=2)
    copyfile(db_tmp_file, db_file)
    os.remove(db_tmp_file)
    bot.send_message(chat_id=update.message.chat_id,
                     text="Se ha eliminado el producto en seguimiento con el ID " + id)
    logging.info("Alfred eliminó el producto en seguimiento con el ID " + id + " a petición del client ID " + str(
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
    log_file = config['AMAZON']['LOG_FILE']
    log_level = config['AMAZON']['LOG_LEVEL']
    db_file = config['AMAZON']['DB_FILE']
    user_agent_list = config['AMAZON']['USER_AGENT_LIST']
    user_agent_hit_file = config['AMAZON']['USER_AGENT_HIT_FILE']
    scraping_max_tries = config['AMAZON']['SCRAPING_MAX_TRIES']
    requests_delay = config['AMAZON']['REQUESTS_DELAY']
    graphite_server = config['AMAZON']['GRAPHITE_SERVER']
    graphite_port = config['AMAZON']['GRAPHITE_PORT']
    graphite_prefix = config['AMAZON']['GRAPHITE_PREFIX']

    # Configurar logger a fichero:
    logging.basicConfig(level=getattr(logging, log_level),
                        format="[%(asctime)s] [%(levelname)s] - [Amazon] - %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                        filename=log_file,
                        filemode='a')

    # Configurar logger a stdout:
    console = logging.StreamHandler()
    console.setLevel(getattr(logging, log_level))
    console.setFormatter(logging.Formatter("[%(levelname)s] - [Amazon] - %(message)s"))
    logging.getLogger('').addHandler(console)

    # Inicio
    logging.info("Inicio del programa")

    # Crear una instancia del bot
    bot = telegram.Bot(token=bot_token)

    # Scrape de los precios de los productos en seguimiento y escritura en Graphite
    graphyte.init(graphite_server, port=graphite_port, prefix=graphite_prefix)
    logging.debug("Obteniendo el precio de cada producto en seguimiento")
    with open(db_file, 'r') as f1:
        items = json.load(f1)
    for item in items['amazon']:
        price = ""
        n_tries = 1
        logging.info("Obteniendo precio del producto: " + item['name'])
        while price == "" and n_tries <= int(scraping_max_tries):
            time.sleep(int(requests_delay))
            user_agent = random.choice(user_agent_list)
            header = {'User-Agent': user_agent}
            logging.debug("Intento: " + str(n_tries) + ", Header: " + header['User-Agent'])
            page = requests.get(item['url'], headers=header)
            soup = BeautifulSoup(page.content, "lxml")
            for divs in soup.find_all("div"):
                try:
                    price = str(divs['data-asin-price'])
                    break
                except:
                    pass
            n_tries += 1
        if price:
            logging.info("Precio de " + item['name'] + " encontrado: " + price + " €")
            with open(user_agent_hit_file, 'a') as f2:
                f2.write(user_agent + "\n")
            # Envio de metricas a Graphite:
            name = item['name']
            metric_prefix = name.replace(" ", "_")
            graphyte.send(metric_prefix, float(price))
        else:
            logging.warning("No se ha podido obtener el precio de " + item['name'])
    # Fin
    logging.info("Fin del programa")


if __name__ == '__main__':
    main()
