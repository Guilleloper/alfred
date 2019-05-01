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
import shutil


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


# Función para obtener el timestamp del primer precio registrado para un producto en seguimiento
def first_timestamp(item_id):

    # Carga de fichero de configuración
    script_path = os.path.dirname(sys.argv[0])
    with open(script_path + '/../config/config.json', 'r') as f:
        config = json.load(f)
    db_file = config['AMAZON']['DB_FILE']
    graphite_server = config['AMAZON']['GRAPHITE_SERVER']
    graphite_api_port = config['AMAZON']['GRAPHITE_API_PORT']
    graphite_prefix = config['AMAZON']['GRAPHITE_PREFIX']
    max_graph_history = config['AMAZON']['MAX_GRAPH_HISTORY']

    # Obtención del timestamp de la primera métrica
    with open(db_file, 'r') as f1:
        items = json.load(f1)
    for item in items['amazon']:
        if int(item_id) == item['id']:
            item_name = item['name']
            metric_prefix = item_name.replace(" ", "_")
            url = "http://" + graphite_server + ":" + graphite_api_port + "/render?target=" + graphite_prefix + "." + metric_prefix + "&from=-" + max_graph_history + "&until=now&format=json"
            page_output = requests.get(url)
            html_output = page_output.content.decode('utf8')
            json_output = json.loads(html_output)
            for datapoint in json_output[0]['datapoints']:
                if datapoint[0] != None:
                    timestamp = datapoint[1]
                    break
    return timestamp

# Función para obtener las estadísticas (valores mínimo, máximo, medio y actual) de un prodcuto en seguimiento
def stats(item_id):

    # Carga de fichero de configuracion
    script_path = os.path.dirname(sys.argv[0])
    with open(script_path + '/../config/config.json', 'r') as f:
        config = json.load(f)
    db_file = config['AMAZON']['DB_FILE']
    graphite_server = config['AMAZON']['GRAPHITE_SERVER']
    graphite_api_port = config['AMAZON']['GRAPHITE_API_PORT']
    graphite_prefix = config['AMAZON']['GRAPHITE_PREFIX']

    # Obtención del timestamp del primer precio registrado para un producto en seguimiento
    logging.debug("Obteniendo timestamp del primer precio registrado para un producto en seguimiento")
    time_from = first_timestamp(item_id)
    logging.debug("Timestamp del primer precio registrado obtenido: " + str(time_from))

    # Obtención de las estadísticas de un producto
    with open(db_file, 'r') as f1:
        items = json.load(f1)
    for item in items['amazon']:
        if int(item_id) == item['id']:
            item_name = item['name']
            metric_prefix = item_name.replace(" ", "_")
            url_min_value = "http://" + graphite_server + ":" + graphite_api_port + "/render?target=aggregateLine(" + graphite_prefix + "." + metric_prefix + ",'min')&from=" + str(time_from) + "&until=now&format=json"
            url_max_value = "http://" + graphite_server + ":" + graphite_api_port + "/render?target=aggregateLine(" + graphite_prefix + "." + metric_prefix + ",'max')&from=" + str(time_from) + "&until=now&format=json"
            url_avg_value = "http://" + graphite_server + ":" + graphite_api_port + "/render?target=aggregateLine(" + graphite_prefix + "." + metric_prefix + ",'avg')&from=" + str(time_from) + "&until=now&format=json"
            url_last_value = "http://" + graphite_server + ":" + graphite_api_port + "/render?target=aggregateLine(" + graphite_prefix + "." + metric_prefix + ",'last')&from=" + str(time_from) + "&until=now&format=json"
            page_min_value = requests.get(url_min_value)
            page_max_value = requests.get(url_max_value)
            page_avg_value = requests.get(url_avg_value)
            page_last_value = requests.get(url_last_value)
            html_min_value = page_min_value.content.decode('utf8')
            html_max_value = page_max_value.content.decode('utf8')
            html_avg_value = page_avg_value.content.decode('utf8')
            html_last_value = page_last_value.content.decode('utf8')
            json_min_value = json.loads(html_min_value)
            json_max_value = json.loads(html_max_value)
            json_avg_value = json.loads(html_avg_value)
            json_last_value = json.loads(html_last_value)
            item_min_value = json_min_value[0]['tags']['name']
            item_max_value = json_max_value[0]['tags']['name']
            item_avg_value = json_avg_value[0]['tags']['name']
            item_last_value = json_last_value[0]['tags']['name']

    item_stats = [item_name, item_min_value, item_max_value, item_avg_value, item_last_value]
    return item_stats


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


# Funcion para obtener el detalle (valores maximo, minimo, medio y actual) de un producto en seguimiento
def detail(bot, update):

    # Comprobaciones previas
    id = update.message.text.replace("/amazon_detail ", "")
    if id == "/amazon_detail":
        bot.send_message(chat_id=update.message.chat_id,
                         text="Para mostrar el detalle de un producto en seguimiento debe proceder como se indica:\n"
                              "  /amazon_detail <ID>")
        return False
    logging.debug("Comprobando identificador de producto en seguimiento antes de mostrar el detalle")
    if not id_hit(id):
        bot.send_message(chat_id=update.message.chat_id,
                         text="No existe ningún producto en seguimiento con el identificador " + id)
        logging.warning(
            "Se ha intentado mostrar el detalle de un producto en seguimiento con un identificador no válido a petición del client ID " + str(
                update.message.chat_id))
        return False
    logging.debug("Identificador de producto en seguimiento encontrado: " + id)

    # Obtener detalle de un producto en seguimiento
    logging.debug("Obteniendo las estadísticas del producto en seguimiento con ID: " + id)
    item_stats = stats(id)
    item_name = item_stats[0]
    item_min_value = item_stats[1]
    item_max_value = item_stats[2]
    item_avg_value = item_stats[3]
    item_last_value = item_stats[4]
    logging.debug("Estadísticas obtenidas para el producto en seguimiento con ID: " + id)

    # Mostrar detalle de un producto en seguimiento
    bot.send_message(chat_id=update.message.chat_id,
                     text="Detalle del producto \"" + item_name + "\":\n"
                          "  Precio mínimo: " + item_min_value + "€\n"
                          "  Precio máximo: " + item_max_value + "€\n"
                          "  Precio medio: " + item_avg_value + "€\n"
                          "  Precio actual: " + item_last_value + "€\n")
    logging.debug("Alfred mostró el detalle del producto en seguimiento con el ID " + id + " a petición del client ID " + str(
        update.message.chat_id))
    return True


# Funcion para obtener la gráfica con el histórico de valores de un producto en seguimiento
def graph(bot, update):

    # Carga de fichero de configuración
    script_path = os.path.dirname(sys.argv[0])
    with open(script_path + '/../config/config.json', 'r') as f:
        config = json.load(f)
    db_file = config['AMAZON']['DB_FILE']
    graph_tmp_file = config['AMAZON']['TMP_PATH'] + "/amazon.png"
    graphite_server = config['AMAZON']['GRAPHITE_SERVER']
    graphite_api_port = config['AMAZON']['GRAPHITE_API_PORT']
    graphite_prefix = config['AMAZON']['GRAPHITE_PREFIX']

    # Comprobaciones previas:
    id = update.message.text.replace("/amazon_graph ", "")
    if id == "/amazon_graph":
        bot.send_message(chat_id=update.message.chat_id,
                         text="Para mostrar el historico de precios de un producto en seguimiento debe proceder como se indica:\n"
                              "  /amazon_graph <ID>")
        return False
    if not id_hit(id):
        bot.send_message(chat_id=update.message.chat_id,
                         text="No existe ningún producto en seguimiento con el identificador " + id)
        logging.warning(
            "Se ha intentado mostrar el histórico de precios de un producto en seguimiento con un identificador no válido a petición del client ID " + str(
                update.message.chat_id))
        return False
    logging.debug("Identificador de producto en seguimiento encontrado: " + id)

    # Obtención del timestamp del primer precio registrado para un producto en seguimiento
    logging.debug("Obteniendo timestamp del primer precio registrado para un producto en seguimiento")
    time_from = first_timestamp(id)
    logging.debug("Timestamp del primer precio registrado obtenido: " + str(time_from))

    # Obtención de la gráfica y generación del fichero de imagen
    logging.debug("Obteniendo la gráfica para el producto en seguimiento con ID " + id)
    with open(db_file, 'r') as f1:
        items = json.load(f1)
    for item in items['amazon']:
        if int(id) == item['id']:
            item_name = item['name']
            metric_prefix = item_name.replace(" ", "_")
            url = "http://" + graphite_server + ":" + graphite_api_port + "/render?target=" + graphite_prefix + "." + metric_prefix + "&from=" + str(time_from) + "&until=now"
            page_output = requests.get(url, stream=True)
            if page_output.status_code != 200:
                logging.warning("No se ha podido descargar la gráfica para el producto en seguimiento con ID " + id)
                return False
            else:
                with open(graph_tmp_file, 'wb') as f2:
                    page_output.raw.decode_content = True
                    shutil.copyfileobj(page_output.raw, f2)
                logging.debug("Gráfica obtenida y almacenada en la ubicación" + graph_tmp_file)
                # Envío de la imagen por chat
                bot.send_photo(chat_id=update.message.chat_id,
                               photo=open(graph_tmp_file, 'rb'))
                logging.debug(
                    "Alfred mostró la gráfica del producto en seguimiento con el ID " + id + " a petición del client ID " + str(
                        update.message.chat_id))

                # Borrar la imagen
                os.remove(graph_tmp_file)
                return True


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

    # Borrado del producto en seguimiento
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
    graphite_carbon_port = config['AMAZON']['GRAPHITE_CARBON_PORT']
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
    graphyte.init(graphite_server, port=graphite_carbon_port, prefix=graphite_prefix)
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
            # Registro de user agent valido para su posterior analisis
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
