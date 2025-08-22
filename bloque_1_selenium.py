from config import URL_BIWENGER_HOME, URL_BIWENGER_LIGA, URL_BIWENGER_PLAYERS
import time
import locale
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from datetime import datetime, date
from collections import Counter
from bloque_bbdd import get_db_connection, obtener_userIds
from utils import traducir_mes, log_message, log_message_with_print
import os
locale.setlocale(locale.LC_TIME, "C")
# Variable global del módulo

def do_login(driver):
    driver.get(URL_BIWENGER_HOME)
    time.sleep(3)  # Esperar a que cargue
    web_element_agree = driver.find_elements(By.ID, 'didomi-notice-agree-button')[0]
    web_element_agree.click()

    web_element_comienzo = driver.find_elements(By.CSS_SELECTOR, 'a.btn.primary.xl[href="/login"]')[0]
    web_element_comienzo.click()

    web_element_cuentaDisponible = driver.find_elements(By.LINK_TEXT, "Ya tengo cuenta")[0]
    web_element_cuentaDisponible.click()

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

def cerrar_modal_password(driver):
    try:
        boton = driver.find_element(By.XPATH, "//button[contains(text(), 'Aceptar')]")
        boton.click()
        print("✅ Popup de contraseña cerrada")
    except:
        print("ℹ️ No se encontró popup de contraseña")

def do_obtener_usuarios(driver):
    time.sleep(1)
    driver.get(URL_BIWENGER_LIGA)
    time.sleep(1)
    usuarios = []
    cards = driver.find_elements(By.CSS_SELECTOR, "user-card")
    for card in cards:
        try:
            # Dentro de cada card, busca el <h3><a> con el nombre de usuario
            enlace = card.find_element(By.CSS_SELECTOR, "div.main h3 a")
            nombre = enlace.text.strip()
            href = enlace.get_attribute("href")
            num_jug = card.find_element(By.CSS_SELECTOR, "div.main h4").text.split(' jug.')[0]

            enlace.click()
            time.sleep(1)
            plantilla_to_ret = []
            plantilla = driver.find_elements(By.CSS_SELECTOR, "player-card")
            for jugador in plantilla:
                nombre_jugador = jugador.find_element(By.CSS_SELECTOR, "div.main h3 a").text.strip()
                plantilla_to_ret.append(nombre_jugador)

            usuario = {
                "name": nombre,
                "url_name": href,
                "num_jug": int(num_jug),
                "plantilla": plantilla_to_ret
            }
            usuarios.append(usuario)
            boton_atras = driver.find_element(By.CSS_SELECTOR, "div.header i")
            boton_atras.click()
            time.sleep(1)
        except:
            continue  # Por si algún user-card no tiene nombre o el selector falla
    log_message(usuarios)
    return usuarios

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
                date_elem = post.find_element(By.CSS_SELECTOR, "div.date")
                date_str = date_elem.get_attribute("title")  # Ej: "29 jul 2025, 13:37:05"
                if not date_str:
                    continue
                post_datetime = traducir_mes(date_str)
                if is_a_valid_post(post) and post_datetime < cutoff_datetime:
                    repetir = False
                    break
                if is_a_valid_post(post):
                    postToRet.append(post)

            except Exception:
                continue
        # Hacemos scroll para cargar más posts
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # Ya no hay más contenido para cargar
            break
        last_height = new_height
    return postToRet

def is_a_valid_post(league_board_post):
    try:
        header_div = league_board_post.find_element(By.CSS_SELECTOR, "div.header.ng-star-inserted")
        h3_element = header_div.find_element(By.TAG_NAME, "h3")
        cardName = h3_element.text.strip()
        return cardName == 'MERCADO DE FICHAJES' or cardName == 'FICHAJES' or cardName == 'CAMBIO DE NOMBRE' or cardName == 'CLÁUSULAS' or cardName == 'ABONOS Y PENALIZACIONES' or cardName == 'MOVIMIENTO DE JUGADORES'
    except Exception as e:
        log_message(f"⚠️ No se pudo encontrar el h3 esperado")

def obtenerMovimientos(posts):
    log_message_with_print("🌐 Obteniendo movimientos a partir de los post...")
    movimientos_to_insert = []
    conn = get_db_connection()
    user_dict = obtener_userIds(conn)
    for i, post in enumerate(posts, start=1):
        try:
            header_div = post.find_element(By.CSS_SELECTOR, "div.header.ng-star-inserted")
            h3_element = header_div.find_element(By.TAG_NAME, "h3")
            date_elem = header_div.find_element(By.CSS_SELECTOR, "div.date")
            date_str = date_elem.get_attribute("title")
            post_datetime = traducir_mes(date_str)

            cardName = h3_element.text.strip()
            if cardName == 'MERCADO DE FICHAJES':
                try:
                    log_message(f"\n📌 Post {i}:")
                    log_message(f"   - {h3_element.text.strip()} ({date_str})")
                    merc_fichajes_div = post.find_element(By.CSS_SELECTOR, "div.content.market")
                    fichajes = merc_fichajes_div.find_elements(By.TAG_NAME, 'li')
                    for fichaje in fichajes:
                        fichajeH3 = fichaje.find_element(By.TAG_NAME, "h3")
                        fichajeName = fichajeH3.text.strip()
                        userlink = fichaje.find_element(By.TAG_NAME, 'user-link')
                        userName = userlink.find_element(By.TAG_NAME, 'a').text.strip()
                        valorCompraStr = fichaje.find_element(By.TAG_NAME, 'strong').text.strip()
                        valor_limpio = valorCompraStr.replace('.', '').replace('€', '').replace(' ', '')
                        valorCompra = int(valor_limpio)
                        log_message(f"      - {fichajeName}: Comprado por {userName} por {valorCompra} €")
                        movimiento = {"usuario_id": user_dict[userName], "tipo":"fichaje", "jugador": fichajeName, "cantidad": -valorCompra, "fecha": str(post_datetime)}
                        movimientos_to_insert.append(movimiento)
                except Exception as e:
                    log_message(f"   ⚠️ Excepcion en MERCADO DE FICHAJES: {e}")
            elif cardName == 'FICHAJES':
                try:
                    log_message(f"\n📌 Post {i}:")
                    log_message(f"   - {h3_element.text.strip()} ({date_str})")
                    if has_header_name(post):
                        userName = get_header_name(post)
                        content_transfer_div = post.find_element(By.CSS_SELECTOR, "div.content.transfer")
                        jugadores_transferidos = content_transfer_div.find_elements(By.TAG_NAME, 'li')
                        for jugador in jugadores_transferidos:
                            jugadorH3 = jugador.find_element(By.TAG_NAME, "h3")
                            jugadorName = jugadorH3.text.strip()
                            valorVentaStr = jugador.find_element(By.TAG_NAME, 'strong').text.strip()
                            valor_limpio = valorVentaStr.replace('.', '').replace('€', '').replace(' ', '')
                            valorVenta = int(valor_limpio)
                            log_message(f"      - {jugadorName}: Vendido por {userName} a Mercado por {valorVenta} €")
                            movimiento = {"usuario_id": user_dict[userName], "tipo":"venta", "jugador": jugadorName, "cantidad": valorVenta, "fecha": str(post_datetime)}
                            movimientos_to_insert.append(movimiento)
                    else:
                        content_transfer_div = post.find_element(By.CSS_SELECTOR, "div.content.transfer")
                        jugadores_transferidos = content_transfer_div.find_elements(By.TAG_NAME, 'li')
                        for jugador in jugadores_transferidos:
                            jugadorH3 = jugador.find_element(By.TAG_NAME, "h3")
                            jugadorName = jugadorH3.text.strip()
                            userNames = get_user_name_fichajes(jugador)
                            userNameVenta = userNames[0]
                            userNameCompra = userNames[1]
                            valorVentaStr = jugador.find_element(By.TAG_NAME, 'strong').text.strip()
                            valor_limpio = valorVentaStr.replace('.', '').replace('€', '').replace(' ', '')
                            valor = int(valor_limpio)
                            log_message(f"      - {jugadorName}: Vendido por {userNameVenta} a {userNameCompra} por {valor} €")

                            movimientoVenta = {"usuario_id": user_dict[userNameVenta], "tipo": "venta", "jugador": jugadorName, "cantidad": valor, "fecha": str(post_datetime)}
                            movimientos_to_insert.append(movimientoVenta)
                            if userNameCompra.lower() != 'mercado':
                                movimientoCompra = {"usuario_id": user_dict[userNameCompra], "tipo": "fichaje", "jugador": jugadorName, "cantidad": -valor, "fecha": str(post_datetime)}
                                movimientos_to_insert.append(movimientoCompra)

                except Exception as e:
                    log_message(f"   ⚠️ Excepcion en FICHAJES: {e}")
            elif cardName == 'CAMBIO DE NOMBRE':
                log_message(f"\n📌 Post {i}:")
                log_message(f"   - {h3_element.text.strip()}")
                content_user_name_div = post.find_element(By.CSS_SELECTOR, "div.content.userName")
                cambioUsuarioLi = content_user_name_div.find_elements(By.TAG_NAME, 'li')[0]
                userlink = cambioUsuarioLi.find_elements(By.TAG_NAME, 'user-link')[1]
                userNameOld = userlink.find_element(By.TAG_NAME, 'a').text.strip()
                userNameNew = cambioUsuarioLi.find_element(By.TAG_NAME, 'strong').text.strip()
                log_message(f"      - {userNameOld} ha cambiado su nombre a {userNameNew}")
            elif cardName == 'CLÁUSULAS':
                try:
                    log_message(f"\n📌 Post {i}:")
                    content_transfer_div = post.find_element(By.CSS_SELECTOR, "div.content.transfer")
                    jugadores_transferidos = content_transfer_div.find_elements(By.TAG_NAME, 'li')
                    for jugador in jugadores_transferidos:
                        jugadorH3 = jugador.find_element(By.TAG_NAME, "h3")
                        fichajeName = jugadorH3.find_element(By.TAG_NAME, "a").text.strip()
                        userNames = get_user_name_clausulas(jugador)
                        userNameVenta = userNames[0]
                        userNameCompra = userNames[1]
                        valorVentaStr = jugador.find_element(By.TAG_NAME, 'strong').text.strip()
                        valor_limpio = valorVentaStr.replace('.', '').replace('€', '').replace(' ', '')
                        valor = int(valor_limpio)
                        log_message(f"      - {userNameCompra} ha pagado la clausula de {fichajeName} a {userNameVenta} por {valor} €")
                        movimientoVenta = {"usuario_id": user_dict[userNameCompra], "tipo": "fichaje", "jugador": fichajeName, "cantidad": -valor, "fecha": str(post_datetime)}
                        movimientos_to_insert.append(movimientoVenta)
                        movimientoCompra = {"usuario_id": user_dict[userNameVenta], "tipo": "clausulazo", "jugador": fichajeName, "cantidad": valor, "fecha": str(post_datetime)}
                        movimientos_to_insert.append(movimientoCompra)
                except Exception as e:
                    log_message(f"   ⚠️ Excepcion en FICHAJES: {e}")
            elif cardName == 'ABONOS Y PENALIZACIONES':
                try:
                    log_message(f"\n📌 Post {i}:")
                    log_message(f"   - {h3_element.text.strip()}")
                    content_bonus_div = post.find_element(By.CSS_SELECTOR, "div.content.bonus")
                    penalizaciones = content_bonus_div.find_elements(By.TAG_NAME, 'tr')
                    for penalizacion in penalizaciones:
                        userlink = penalizacion.find_element(By.TAG_NAME, 'user-link')
                        userName = userlink.find_element(By.TAG_NAME, 'a').text.strip()
                        decrement = post.find_element(By.CSS_SELECTOR, "increment.decrement.icon.icon-decrement").text.strip()
                        valor_limpio = decrement.replace('.', '').replace('€', '').replace(' ', '')
                        valor = int(valor_limpio)
                        log_message(f"      - {userName} ha sido penalizado por el administrador con {valor} €")
                        movimientoPenalizacion = {"usuario_id": user_dict[userName], "tipo": "penalizacion", "jugador": "", "cantidad": -valor, "fecha": str(post_datetime)}
                        movimientos_to_insert.append(movimientoPenalizacion)
                except Exception as e:
                    log_message(f"   ⚠️ Excepcion en FICHAJES: {e}")
        except Exception as e:
            log_message(f"   ⚠️ No se pudo encontrar el h3 esperado: {e}")
    return movimientos_to_insert

def obtener_movimientos_abonos(driver, user_dict):
    select_element = driver.find_element(By.CSS_SELECTOR, "div.tools select.pl")
    select_obj = Select(select_element)
    select_obj.select_by_visible_text("Jornadas")
    time.sleep(2)
    moviemientos_abonos = []
    try:
        all_posts = driver.find_elements(By.CSS_SELECTOR, 'league-board-post')
        last_post = all_posts[0]
        numero_de_jornada = last_post.find_element(By.CSS_SELECTOR, "h3 a").text.strip()
        time_relative = last_post.find_element(By.CSS_SELECTOR, "time-relative")
        fecha_sin_formato = time_relative.get_attribute("title")
        post_date = datetime.strptime(fecha_sin_formato, "%d/%m/%y, %H:%M")
        tr_list = last_post.find_elements(By.CSS_SELECTOR, 'div.content tr')
        for row in tr_list:
            td_list = row.find_elements(By.CSS_SELECTOR, 'td')
            user_name = td_list[1].find_element(By.CSS_SELECTOR, "a").text
            valor = td_list[3].find_element(By.CSS_SELECTOR, "increment").text.replace(" €", "").replace(".", "")
            abono = {'usuario_id': user_dict[user_name], 'tipo': 'abono', 'jugador': numero_de_jornada, 'cantidad': int(valor), 'fecha': str(post_date)}
            moviemientos_abonos.append(abono)
    except Exception as e:
        print("❌ El div.prueba no existe en el primer card")
    return moviemientos_abonos

def has_header_name(post):
    hasHeaderName = True
    try:
        header_div = post.find_element(By.CSS_SELECTOR, "div.header.ng-star-inserted")
        userlink = header_div.find_element(By.TAG_NAME, 'user-link')
        userlink.find_element(By.TAG_NAME, 'a').text.strip()
    except Exception as e:
        hasHeaderName = False
    return hasHeaderName

def get_header_name(post):
    header_div = post.find_element(By.CSS_SELECTOR, "div.header.ng-star-inserted")
    userlink = header_div.find_element(By.TAG_NAME, 'user-link')
    return userlink.find_element(By.TAG_NAME, 'a').text.strip()

def get_user_name_fichajes(jugador):
    try:
        userNames = []
        from_to_div = jugador.find_element(By.CSS_SELECTOR, "div.from-to")
        userlinks = from_to_div.find_elements(By.TAG_NAME, 'user-link')
        if len(userlinks) == 2:
            name1 = userlinks[0].find_element(By.TAG_NAME, 'a').text.strip()
            name2 = userlinks[1].find_element(By.TAG_NAME, 'a').text.strip()
            userNames.append(name1)
            userNames.append(name2)
        elif len(userlinks) == 1:
            name1 = userlinks[0].find_element(By.TAG_NAME, 'a').text.strip()
            name2 = from_to_div.find_element(By.TAG_NAME, 'em').text.strip()
            userNames.append(name1)
            userNames.append(name2)
    except Exception as e:
        log_message(f"   ⚠️ Excepcion en get_user_name_fichajes: {e}")
    return userNames

def get_user_name_clausulas(jugador):
    try:
        userNames = []
        from_to_div = jugador.find_element(By.CSS_SELECTOR, "div.from-to")
        userlinks = from_to_div.find_elements(By.TAG_NAME, 'user-link')
        userNameVenta = userlinks[0].find_element(By.TAG_NAME, 'a').text.strip()
        userNameCompra = userlinks[1].find_element(By.TAG_NAME, 'a').text.strip()
        userNames.append(userNameVenta)
        userNames.append(userNameCompra)
    except Exception as e:
        log_message(f"   ⚠️ Excepcion en get_user_name_clausulas: {e}")
    return userNames

def analize_user_name(userName):
    userToRet = ''
    if isinstance(userName, list):
        listaUsuarios = []
        for movement in userName:
            partes = movement.split("-->")
            listaUsuarios.append(partes[0])
            listaUsuarios.append(partes[1])
        userToRet = get_user_repited(listaUsuarios)
    else:
        userToRet = userName

    return userToRet

def get_user_repited(listNames):
    # Contamos las ocurrencias
    conteo = Counter(listNames)
    # Eliminamos la clave 'Mercado' si existe
    conteo.pop("Mercado", None)
    # Obtenemos el string con más ocurrencias
    if conteo:
        return conteo.most_common(1)[0][0]
    else:
        return None  # Por si el array está vacío o solo tenía "Mercado"

def number_of_players(driver):
    driver.get(URL_BIWENGER_PLAYERS)
    time.sleep(1)
    total_jugadores = int(driver.find_element(By.CSS_SELECTOR, 'pagination span').text.split('de ')[1])
    print(total_jugadores)
    return int(total_jugadores)
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
    for fila in filas:
        try:
            nombre = fila.find_element(By.CSS_SELECTOR, ".main h3 a").text.strip()
            valor = int(fila.find_element(By.CSS_SELECTOR, ".main h4").text.replace('€', '').replace('.', '').strip())
            posicion = fila.find_element(By.CSS_SELECTOR, "player-position").get_attribute("title")
            equipo = fila.find_element(By.CSS_SELECTOR, "div.team-pos a").get_attribute("title")

            jugador_info = {"nombre": nombre, "valor": valor, "posicion": posicion, "equipo": equipo}
            print(jugador_info)
            jugadores.append(jugador_info)
        except Exception as e:
            print(f"Error extrayendo jugador: {e}")

    return jugadores