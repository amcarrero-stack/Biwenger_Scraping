from config import URL_BIWENGER_HOME, URL_BIWENGER_LIGA, URL_BIWENGER_PLAYERS
import time
import locale
import re
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from datetime import datetime, date
from collections import Counter
from bloque_bbdd import get_db_connection, obtener_userIds, obtener_registros_tabla, obtener_jugadores_dict
from utils import traducir_mes, log_message, log_message_with_print
import os
from wrappers import Post, Ventas, Fichajes, Clausulazos, Abonos, Penalizaciones, Movimientos
locale.setlocale(locale.LC_TIME, "C")
# Variable global del módulo

def do_login(driver):
    log_message_with_print("🌐 Navegando a la página principal de Biwenger...")
    driver.get(URL_BIWENGER_HOME)
    time.sleep(3)  # Esperar a que cargue
    web_element_agree = driver.find_elements(By.ID, 'didomi-notice-agree-button')[0]
    web_element_agree.click()
    time.sleep(1)
    web_element_comienzo = driver.find_elements(By.CSS_SELECTOR, 'a.btn.primary.xl[href="/login"]')[0]
    web_element_comienzo.click()
    time.sleep(1)
    web_element_cuentaDisponible = driver.find_elements(By.LINK_TEXT, "Ya tengo cuenta")[0]
    web_element_cuentaDisponible.click()
    time.sleep(1)
    # 👇 Leer credenciales de variables de entorno
    email = os.getenv("BIWENGER_USER")
    password = os.getenv("BIWENGER_PASS")

    web_element_email_input = driver.find_elements(By.NAME, 'email')[0]
    web_element_email_input.send_keys(email)

    web_element_email_input = driver.find_elements(By.NAME, 'password')[0]
    web_element_email_input.send_keys(password)
    time.sleep(3)

    web_element_boton_login = driver.find_elements(By.CSS_SELECTOR, 'button.btn.squared')[0]
    web_element_boton_login.click()

def obtener_usuarios_web(driver):
    """Devuelve lista de usuarios con nombre, url, nº de jugadores y plantilla"""
    driver.get(URL_BIWENGER_LIGA)
    time.sleep(1)
    usuarios = []

    for card in driver.find_elements(By.CSS_SELECTOR, "user-card"):
        usuario = parse_user_card(driver, card)
        if usuario:
            usuarios.append(usuario)
    return usuarios

def parse_user_card(driver, card):
    """Parsea un user-card y devuelve dict usuario"""
    try:
        enlace = card.find_element(By.CSS_SELECTOR, "div.main h3 a")
        nombre = enlace.text.strip()
        href = enlace.get_attribute("href")
        num_jug = int(card.find_element(By.CSS_SELECTOR, "div.main h4").text.split(' jug.')[0])

        enlace.click()
        time.sleep(1)
        plantilla = [j.text.strip() for j in driver.find_elements(By.CSS_SELECTOR, "player-card div.main h3 a")]

        driver.find_element(By.CSS_SELECTOR, "div.header i").click()
        time.sleep(1)

        return {"name": nombre, "url_name": href, "num_jug": num_jug, "plantilla": plantilla}
    except:
        return None


def get_posts_until_date(driver, cutoff_datetime):
    log_message_with_print("🌐 Obteniendo post...")
    driver.get(URL_BIWENGER_HOME)
    last_height = driver.execute_script("return document.body.scrollHeight")
    repetir = True
    postToRet = []
    while repetir:
        time.sleep(1)
        all_posts = driver.find_elements(By.CSS_SELECTOR, 'league-board-post')
        log_message_with_print(f'all_posts len es: {len(all_posts)}')
        postToRet = []
        for post in all_posts:
            try:
                header_div = post.find_element(By.CSS_SELECTOR, "div.header.ng-star-inserted")
                h3_element = header_div.find_element(By.TAG_NAME, "h3")
                cardName = h3_element.text.strip()
                date_elem = header_div.find_element(By.CSS_SELECTOR, "div.date")
                date_str = date_elem.get_attribute("title")  # Ej: "29 jul 2025, 13:37:05"
                if not date_str:
                    continue
                post_datetime = traducir_mes(date_str)
                validPost = is_a_valid_post(cardName)
                if validPost and post_datetime < cutoff_datetime:
                    repetir = False
                    break
                if validPost:
                    postToRet.append(post)

            except Exception as e:
                error_message = e.__str__()
                patron = r'(\{"method":".*?"\})'
                coincidencia = re.search(patron, error_message)

                if coincidencia:
                    json_str_obj = json.loads(coincidencia.group(1))
                    if json_str_obj['method'] == 'css selector' and json_str_obj['selector'] == 'div.header.ng-star-inserted' and "Fin de" in post.find_element(By.CSS_SELECTOR, "div.panel-header h3").text.strip():
                        postToRet.append(post)
                continue
        # Hacemos scroll para cargar más posts
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # Ya no hay más contenido para cargar
            break
        last_height = new_height
    log_message(f"Se han recogido {len(postToRet)} movimientos hasta {cutoff_datetime}")
    return postToRet

def is_a_valid_post(cardName):
    return cardName == 'MERCADO DE FICHAJES' or cardName == 'FICHAJES' or cardName == 'CAMBIO DE NOMBRE' or cardName == 'CLÁUSULAS' or cardName == 'ABONOS Y PENALIZACIONES' or cardName == 'MOVIMIENTO DE JUGADORES'

def obtener_posts_wrapper(posts):
    log_message_with_print("🌐 Obteniendo posts wrapper a partir de los post...")
    post_wrapper_list = []
    for i, post in enumerate(posts, start=1):
        post_wrapper_list.append(Post(post))
    return post_wrapper_list

def obtener_movimientos_de_jugadores(conn, jugadores_actuales, modification_date):
    jugadores_dict = obtener_jugadores_dict(jugadores_actuales)
    modification_date_str = modification_date.strftime("%Y-%m-%d %H:%M:%S")
    fecha_hoy = datetime.today().replace(microsecond=0)
    fecha_hoy_str = fecha_hoy.strftime("%Y-%m-%d %H:%M:%S")
    movimientos_bbdd = obtener_registros_tabla(conn, 'movimientos', ['id', 'jugador', 'accion'], f"tipo='movimiento' AND fecha >= '{modification_date_str}' AND fecha <= '{fecha_hoy_str}'",'')
    log_message_with_print("🌐 Obteniendo movimientos jugadores a partir de los post...")
    movimientos_jugadores = []
    movimientos_to_insert =[]
    movimientos_to_delete = []
    movimientos_to_update = []
    for movimiento in movimientos_bbdd:
        player_name = movimiento['jugador']
        accion = movimiento['accion'].strip()
        if "ha abandonado" in accion:
            movimientos_to_delete.append(jugadores_dict[player_name])
            print(f'El jugador {player_name} ha abandonado la competicion')
            continue
        if "fichado por" in accion:
            nombre_equipo = accion.split('fichado por ')[1]
            movimiento = {"nombre": player_name, "equipo": nombre_equipo}
            movimientos_to_insert.append(movimiento)
        if "transferido de" in accion:
            equipos = accion.split('transferido de ')[1]
            nombre_equipo = equipos.split(' a ')[1]
            movimiento = {"id": jugadores_dict[player_name], "nombre": player_name, "equipo": nombre_equipo}
            movimientos_to_update.append(movimiento)


    print(f'movimientos_to_delete es: {movimientos_to_delete}')
    if movimientos_to_delete:
        movimientos_jugadores.append({"recordsToDelete": movimientos_to_delete})
    print(f'movimientos_to_insert es: {movimientos_to_insert}')
    if movimientos_to_insert:
        movimientos_jugadores.append({"recordsToInsert": movimientos_to_insert})
    print(f'movimientos_to_update es: {movimientos_to_update}')
    if movimientos_to_update:
        movimientos_jugadores.append({"recordsToUpdate": movimientos_to_update})

    return movimientos_jugadores

def set_all_players(driver):
    driver.get(URL_BIWENGER_PLAYERS)
    time.sleep(3)
    jugadores = []

    while True:
        try:
            jugadores += add_players(driver)
            # Buscar todos los <li> de la paginación
            botones_li = driver.find_elements(By.CSS_SELECTOR, "pagination ul li")
            boton_siguiente = None

            for li in botones_li:
                enlace = li.find_element(By.TAG_NAME, "a")
                if enlace.text.strip() == "›":
                    boton_siguiente = li
                    break

            if boton_siguiente:
                # Aquí comprobamos la clase del <li>, no del <a>
                if "disabled" in boton_siguiente.get_attribute("class"):
                    break
                else:
                    enlace = boton_siguiente.find_element(By.TAG_NAME, "a")
                    enlace.click()
                    time.sleep(2)
            else:
                break
        except Exception as e:
            print(f"Error en paginación: {e}")
            break

    print(f"Se han extraído {len(jugadores)} jugadores.")
    print(jugadores)
    return jugadores

def add_players(driver):
    jugadores = []
    # Extraer jugadores de la página actual
    filas = driver.find_elements(By.CSS_SELECTOR, "player-list player-card")
    fecha_hoy = datetime.today().replace(microsecond=0)
    for fila in filas:
        try:
            tag_a = fila.find_element(By.CSS_SELECTOR, ".main h3 a")
            nombre = tag_a.text.strip()
            href = tag_a.get_attribute("href")

            valor = int(fila.find_element(By.CSS_SELECTOR, ".main h4").text.replace('€', '').replace('.', '').strip())
            posicion = fila.find_element(By.CSS_SELECTOR, "player-position").get_attribute("title")
            equipo = fila.find_element(By.CSS_SELECTOR, "div.team-pos a").get_attribute("title")

            jugador_info = {"nombre": nombre, "valor": valor, "posicion": posicion, "equipo": equipo, "href": href, "modificationDate": str(fecha_hoy)}
            print(jugador_info)
            jugadores.append(jugador_info)
        except Exception as e:
            print(f"Error extrayendo jugador: {e}")

    return jugadores

def procesar_venta(venta, fecha, user_dict):
    accion = venta.accion
    movimientos = []
    if "Cambia por" in accion:
        string_valor_y_jugadores = accion.split('Cambia por ')[1]
        valor_string = string_valor_y_jugadores.split(' de ')[0]
        valor_limpio = valor_string.replace('.', '').replace('€', '').replace(' ', '')
        valor = int(valor_limpio)
        userNameVenta = string_valor_y_jugadores.split(' de ')[1].split(' a ')[0].strip()
        userNameCompra = string_valor_y_jugadores.split(' de ')[1].split(' a ')[1].strip()

        movimientos.append({"usuario_id": user_dict[userNameVenta], "tipo": "venta", "jugador": venta.nombre_jugador,"cantidad": valor, "fecha": str(fecha)})
        if "Mercado" not in userNameCompra:
            movimientos.append({"usuario_id": user_dict[userNameCompra], "tipo": "fichaje", "jugador": venta.nombre_jugador, "cantidad": -valor, "fecha": str(fecha)})

    if "Vendido por" in accion:
        string_valor_y_jugadores = accion.split('Vendido por ')[1]
        userNameVenta = string_valor_y_jugadores.split(' a ')[0].strip()
        compra_y_valor = string_valor_y_jugadores.split(' a ')[1].strip()
        userNameCompra = compra_y_valor.split(' por ')[0]
        valor_string = compra_y_valor.split(' por ')[1]
        valor_limpio = valor_string.replace('.', '').replace('€', '').replace(' ', '')
        valor = int(valor_limpio)

        movimientos.append({"usuario_id": user_dict[userNameVenta], "tipo": "venta", "jugador": venta.nombre_jugador, "cantidad": valor, "fecha": str(fecha)})
        if "Mercado" not in userNameCompra:
            movimientos.append({"usuario_id": user_dict[userNameCompra], "tipo": "fichaje", "jugador": venta.nombre_jugador, "cantidad": -valor, "fecha": str(fecha)})

    return movimientos
def procesar_fichaje(fichaje, fecha, user_dict):
    accion = fichaje.accion
    movimientos = []
    if "Cambia por" in accion:
        string_valor_y_jugadores = accion.split('Cambia por ')[1]
        valor_string = string_valor_y_jugadores.split(' a ')[0]
        valor_limpio = valor_string.replace('.', '').replace('€', '').replace(' ', '')
        valor = int(valor_limpio)
        userNameCompra = string_valor_y_jugadores.split(' a ')[1].strip()

        movimientos.append({"usuario_id": user_dict[userNameCompra], "tipo": "fichaje", "jugador": fichaje.nombre_jugador, "cantidad": -valor, "fecha": str(fecha)})

    return movimientos

def procesar_clausulazo(clausulazo, fecha, user_dict):
    accion = clausulazo.accion
    movimientos = []
    if " ha pagado la cláusula de rescisión de " in accion:
        userNameCompra = accion.split(' ha pagado la cláusula de rescisión de ')[0]
        string_valor_y_jugador_afectado = accion.split(' ha pagado la cláusula de rescisión de ')[1]
        valor_string = string_valor_y_jugador_afectado.split(' a ')[0]
        valor_limpio = valor_string.replace('.', '').replace('€', '').replace(' ', '')
        valor = int(valor_limpio)
        userNameVenta = string_valor_y_jugador_afectado.split(' a ')[1].strip()

        movimientos.append({"usuario_id": user_dict[userNameVenta], "tipo": "clausulazo", "jugador": clausulazo.nombre_jugador, "cantidad": valor, "fecha": str(fecha)})
        movimientos.append({"usuario_id": user_dict[userNameCompra], "tipo": "fichaje", "jugador": clausulazo.nombre_jugador, "cantidad": -valor, "fecha": str(fecha)})

    return movimientos

def procesar_abono(abono, fecha, user_dict):
    accion = abono.accion
    movimientos = []
    if " obtiene " in accion:
        userNameAbonado = accion.split(' obtiene ')[0]
        valor_string = accion.split(' obtiene ')[1]
        valor = int(valor_string)

        movimientos.append({"usuario_id": user_dict[userNameAbonado], "tipo": "abono", "accion": abono.nombre_jugador, "cantidad": valor, "fecha": str(fecha)})

    return movimientos

def procesar_penalizacion(penalizacion, fecha, user_dict):
    accion = penalizacion.accion
    movimientos = []
    if " es penalizado con " in accion:
        userNamePenalizado = accion.split(' es penalizado con ')[0]
        valor_string = accion.split(' es penalizado con ')[1]
        valor = int(valor_string)

        movimientos.append({"usuario_id": user_dict[userNamePenalizado], "tipo": "penalizacion", "jugador": '', "cantidad": -valor, "fecha": str(fecha)})

    return movimientos

def procesar_movimientos(movimiento, fecha, user_dict):
    accion = movimiento.accion
    nombre_jugador = movimiento.nombre_jugador
    movimientos_list = []
    movimientos_list.append({"tipo": "movimiento", "jugador": nombre_jugador, "accion": accion, "cantidad": 0, "fecha": str(fecha)})
    return movimientos_list


POST_PROCESSORS = {
    'Ventas': procesar_venta,
    'Fichajes': procesar_fichaje,
    'Clausulazos': procesar_clausulazo,
    'Abonos': procesar_abono,
    'Penalizaciones': procesar_penalizacion,
    'Movimientos': procesar_movimientos,
}

def procesar_posts_wrapper(posts_wrapper, user_dict):
    movimientos = []

    for post in posts_wrapper:
        try:
            post_type = type(post.post_returned).__name__
            processor = POST_PROCESSORS.get(post_type)
            if processor:
                fecha = post.post_returned.fecha
                items = getattr(post.post_returned, post_type.lower(), [])
                for item in items:
                    movimientos += processor(item, fecha, user_dict)
        except Exception as e:
            print(f"⚠️ Error procesando post: {e}")
    log_message(f'movimientos to insert es {movimientos}')
    return movimientos