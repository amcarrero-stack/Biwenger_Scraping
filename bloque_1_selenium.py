from config import URL_BIWENGER_HOME, NOMBRE_MI_EQUIPO, URL_BIWENGER_LIGA
import time
import locale
from selenium.webdriver.common.by import By
from datetime import datetime, date
from collections import Counter
from bloque_bbdd import get_db_connection, obtener_userId

def do_login(driver):
    driver.get(URL_BIWENGER_HOME)
    time.sleep(3)  # Esperar a que cargue
    web_element_agree = driver.find_elements(By.ID, 'didomi-notice-agree-button')[0]
    web_element_agree.click()

    web_element_comienzo = driver.find_elements(By.CSS_SELECTOR, 'a.btn.primary.xl[href="/login"]')[0]
    web_element_comienzo.click()

    web_element_cuentaDisponible = driver.find_elements(By.LINK_TEXT, "Ya tengo cuenta")[0]
    web_element_cuentaDisponible.click()

    web_element_email_input = driver.find_elements(By.NAME, 'email')[0]
    web_element_email_input.send_keys("amcarrero@gmail.com")

    web_element_email_input = driver.find_elements(By.NAME, 'password')[0]
    web_element_email_input.send_keys("Carrero1110")
    time.sleep(3)

    web_element_boton_login = driver.find_elements(By.CSS_SELECTOR, 'button.btn.squared')[0]
    web_element_boton_login.click()

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

            usuario = {
                "name": nombre,
                "url_name": href,
                "num_jug": int(num_jug)
            }
            usuarios.append(usuario)
        except:
            continue  # Por si algún user-card no tiene nombre o el selector falla
    print(usuarios)
    return usuarios

def get_posts_until_date(driver, modification_date):
    locale.setlocale(locale.LC_TIME, "C")
    print('entra en get_posts_until_date')
    driver.get(URL_BIWENGER_HOME)
    fecha_str_traducida = traducir_mes(modification_date)
    cutoff_datetime = datetime.strptime(fecha_str_traducida, "%d %b %Y")
    last_height = driver.execute_script("return document.body.scrollHeight")
    postToOld = []
    while True:
        time.sleep(1)
        all_posts = cleanPosts(driver.find_elements(By.CSS_SELECTOR, 'league-board-post'))
        print(f'all_posts len es: {len(all_posts)}')
        postToRet = []
        for post in all_posts:
            try:
                date_elem = post.find_element(By.CSS_SELECTOR, "div.date")
                date_str = date_elem.get_attribute("title").split(',')[0]  # Ej: "29 jul 2025, 13:37:05"
                if not date_str:
                    continue
                fecha_str_traducida = traducir_mes(date_str)
                post_datetime = datetime.strptime(fecha_str_traducida, "%d %b %Y")
                is_a_valid_post = check_league_board_post(post)

                if not is_a_valid_post and post_datetime >= cutoff_datetime:
                    continue
                elif post_datetime >= cutoff_datetime:
                    postToRet.append(post)
                else:
                    return postToRet

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
    return postToOld

def cleanPosts(all_posts):
    hoy = date.today()
    firstIteration = True
    postToRet = []
    for post in all_posts:
        try:
            date_elem = post.find_element(By.CSS_SELECTOR, "div.date")
            date_str = date_elem.get_attribute("title").split(',')[0]  # Ej: "29 jul 2025, 13:37:05"
            fecha_str_traducida = traducir_mes(date_str)
            post_datetime = datetime.strptime(fecha_str_traducida, "%d %b %Y")
            post_date = post_datetime.date()

            if firstIteration:
                if post_date < hoy:
                    continue
                else:
                    firstIteration = False
                    postToRet.append(post)
                    continue
            else:
                postToRet.append(post)
        except Exception as e:
            print(f"⚠️ Excepcion en cleanPosts")

    return postToRet

def check_league_board_post(league_board_post):
    try:
        header_div = league_board_post.find_element(By.CSS_SELECTOR, "div.header.ng-star-inserted")
        h3_element = header_div.find_element(By.TAG_NAME, "h3")
        cardName = h3_element.text.strip()
        return cardName == 'MERCADO DE FICHAJES' or cardName == 'FICHAJES' or cardName == 'CAMBIO DE NOMBRE' or cardName == 'CLÁUSULAS' or cardName == 'ABONOS Y PENALIZACIONES'
    except Exception as e:
        print(f"⚠️ No se pudo encontrar el h3 esperado")

def traducir_mes(mes_es):
    traducciones = {
        "ene": "Jan", "feb": "Feb", "mar": "Mar", "abr": "Apr",
        "may": "May", "jun": "Jun", "jul": "Jul", "ago": "Aug",
        "sep": "Sep", "oct": "Oct", "nov": "Nov", "dic": "Dec"
    }
    for esp, eng in traducciones.items():
        mes_es = mes_es.replace(f" {esp} ", f" {eng} ")
    return mes_es
def mostrar_texto_h3(posts):
    movimientos_to_insert = []
    conn = get_db_connection()
    user_dict = obtener_userId(conn)
    for i, post in enumerate(posts, start=1):
        try:
            header_div = post.find_element(By.CSS_SELECTOR, "div.header.ng-star-inserted")
            h3_element = header_div.find_element(By.TAG_NAME, "h3")
            date_elem = header_div.find_element(By.CSS_SELECTOR, "div.date")
            date_str = date_elem.get_attribute("title").split(',')[0]

            cardName = h3_element.text.strip()
            # print(f'{cardName} ({date_str})')
            if cardName == 'MERCADO DE FICHAJES':
                try:
                    print(f"\n📌 Post {i}:")
                    print(f"   - {h3_element.text.strip()} ({date_str})")
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
                        print(f"      - {fichajeName}: Comprado por {userName} por {valorCompra} €")
                        movimiento = {"usuario_id": user_dict[userName], "tipo":"fichaje", "jugador": fichajeName, "cantidad": -valorCompra, "fecha":str(date_str)}
                        movimientos_to_insert.append(movimiento)
                except Exception as e:
                    print(f"   ⚠️ Excepcion en MERCADO DE FICHAJES: {e}")
            elif cardName == 'FICHAJES':
                try:
                    print(f"\n📌 Post {i}:")
                    print(f"   - {h3_element.text.strip()} ({date_str})")
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
                            print(f"      - {jugadorName}: Vendido por {userName} a Mercado por {valorVenta} €")
                            movimiento = {"usuario_id": user_dict[userName], "tipo":"venta", "jugador": jugadorName, "cantidad": valorVenta, "fecha":str(date_str)}
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
                            print(f"      - {jugadorName}: Vendido por {userNameVenta} a {userNameCompra} por {valor} €")

                            movimientoVenta = {"usuario_id": user_dict[userNameVenta], "tipo": "venta", "jugador": jugadorName, "cantidad": valor, "fecha": str(date_str)}
                            movimientos_to_insert.append(movimientoVenta)
                            if userNameCompra.lower() != 'mercado':
                                movimientoCompra = {"usuario_id": user_dict[userNameCompra], "tipo": "fichaje", "jugador": jugadorName, "cantidad": -valor, "fecha": str(date_str)}
                                movimientos_to_insert.append(movimientoCompra)

                except Exception as e:
                    print(f"   ⚠️ Excepcion en FICHAJES: {e}")
            elif cardName == 'CAMBIO DE NOMBRE':
                print(f"\n📌 Post {i}:")
                print(f"   - {h3_element.text.strip()}")
                content_user_name_div = post.find_element(By.CSS_SELECTOR, "div.content.userName")
                cambioUsuarioLi = content_user_name_div.find_elements(By.TAG_NAME, 'li')[0]
                userlink = cambioUsuarioLi.find_elements(By.TAG_NAME, 'user-link')[1]
                userNameOld = userlink.find_element(By.TAG_NAME, 'a').text.strip()
                userNameNew = cambioUsuarioLi.find_element(By.TAG_NAME, 'strong').text.strip()
                print(f"      - {userNameOld} ha cambiado su nombre a {userNameNew}")
            elif cardName == 'CLÁUSULAS':
                try:
                    print(f"\n📌 Post {i}:")
                    content_transfer_div = post.find_element(By.CSS_SELECTOR, "div.content.transfer")
                    jugadores_transferidos = content_transfer_div.find_elements(By.TAG_NAME, 'li')
                    for jugador in jugadores_transferidos:
                        jugadorH3 = jugador.find_element(By.TAG_NAME, "h3")
                        fichajeName = jugadorH3.find_element(By.TAG_NAME, "a").text.strip()
                        userNames = get_user_name_clausulas(post)
                        userNameVenta = userNames[0]
                        userNameCompra = userNames[1]
                        valorVentaStr = jugador.find_element(By.TAG_NAME, 'strong').text.strip()
                        valor_limpio = valorVentaStr.replace('.', '').replace('€', '').replace(' ', '')
                        valor = int(valor_limpio)
                        print(f"      - {userNameCompra} ha pagado la clausula de {fichajeName} a {userNameVenta} por {valor} €")
                        movimientoVenta = {"usuario_id": user_dict[userNameCompra], "tipo": "fichaje", "jugador": fichajeName, "cantidad": -valor, "fecha": str(date_str)}
                        movimientos_to_insert.append(movimientoVenta)
                        movimientoCompra = {"usuario_id": user_dict[userNameVenta], "tipo": "clausulazo", "jugador": fichajeName, "cantidad": valor, "fecha": str(date_str)}
                        movimientos_to_insert.append(movimientoCompra)
                except Exception as e:
                    print(f"   ⚠️ Excepcion en FICHAJES: {e}")
            elif cardName == 'ABONOS Y PENALIZACIONES':
                try:
                    print(f"\n📌 Post {i}:")
                    print(f"   - {h3_element.text.strip()}")
                    content_bonus_div = post.find_element(By.CSS_SELECTOR, "div.content.bonus")
                    penalizaciones = content_bonus_div.find_elements(By.TAG_NAME, 'tr')
                    for penalizacion in penalizaciones:
                        userlink = penalizacion.find_element(By.TAG_NAME, 'user-link')
                        userName = userlink.find_element(By.TAG_NAME, 'a').text.strip()
                        decrement = post.find_element(By.CSS_SELECTOR, "increment.decrement.icon.icon-decrement").text.strip()
                        valor_limpio = decrement.replace('.', '').replace('€', '').replace(' ', '')
                        valor = int(valor_limpio)
                        print(f"      - {userName} ha sido penalizado por el administrador con {valor} €")
                        movimientoPenalizacion = {"usuario_id": user_dict[userName], "tipo": "penalizacion", "jugador": "", "cantidad": -valor, "fecha": str(date_str)}
                        movimientos_to_insert.append(movimientoPenalizacion)
                except Exception as e:
                    print(f"   ⚠️ Excepcion en FICHAJES: {e}")
        except Exception as e:
            print(f"   ⚠️ No se pudo encontrar el h3 esperado: {e}")
    return movimientos_to_insert

def obtener_ventas_y_compras(posts):
    resumen_usuarios = {}

    for i, post in enumerate(posts, start=1):
        try:
            header_div = post.find_element(By.CSS_SELECTOR, "div.header.ng-star-inserted")
            h3_element = header_div.find_element(By.TAG_NAME, "h3")
            date_elem = header_div.find_element(By.CSS_SELECTOR, "div.date")
            date_str = date_elem.get_attribute("title").split(',')[0]

            cardName = h3_element.text.strip()

            if cardName == 'MERCADO DE FICHAJES':
                merc_fichajes_div = post.find_element(By.CSS_SELECTOR, "div.content.market")
                fichajes = merc_fichajes_div.find_elements(By.TAG_NAME, 'li')
                for fichaje in fichajes:
                    userlink = fichaje.find_element(By.TAG_NAME, 'user-link')
                    userName = userlink.find_element(By.TAG_NAME, 'a').text.strip()
                    valorCompraStr = fichaje.find_element(By.TAG_NAME, 'strong').text.strip()
                    valor_limpio = valorCompraStr.replace('.', '').replace('€', '').replace(' ', '')
                    valorCompra = int(valor_limpio)

                    if userName not in resumen_usuarios:
                        resumen_usuarios[userName] = {"username": userName, "compras": 0, "ventas": 0, "penalizaciones": 0}
                    resumen_usuarios[userName]["compras"] += valorCompra

            elif cardName == 'FICHAJES':
                try:
                    if has_header_name(post):
                        userName = get_header_name(post)
                        content_transfer_div = post.find_element(By.CSS_SELECTOR, "div.content.transfer")
                        jugadores_transferidos = content_transfer_div.find_elements(By.TAG_NAME, 'li')
                        for jugador in jugadores_transferidos:
                            valorVentaStr = jugador.find_element(By.TAG_NAME, 'strong').text.strip()
                            valor_limpio = valorVentaStr.replace('.', '').replace('€', '').replace(' ', '')
                            valorVenta = int(valor_limpio)

                            if userName not in resumen_usuarios:
                                resumen_usuarios[userName] = {"username": userName, "compras": 0, "ventas": 0, "penalizaciones": 0}
                            resumen_usuarios[userName]["ventas"] += valorVenta
                    else:
                        content_transfer_div = post.find_element(By.CSS_SELECTOR, "div.content.transfer")
                        jugadores_transferidos = content_transfer_div.find_elements(By.TAG_NAME, 'li')
                        for jugador in jugadores_transferidos:
                            userNames = get_user_name_fichajes(jugador)
                            userNameVenta = userNames[0]
                            userNameCompra = userNames[1]
                            valorVentaStr = jugador.find_element(By.TAG_NAME, 'strong').text.strip()
                            valor_limpio = valorVentaStr.replace('.', '').replace('€', '').replace(' ', '')
                            valor = int(valor_limpio)

                            if userNameVenta not in resumen_usuarios:
                                resumen_usuarios[userNameVenta] = {"username": userNameVenta, "compras": 0, "ventas": 0, "penalizaciones": 0}
                            resumen_usuarios[userNameVenta]["ventas"] += valor

                            if userNameCompra.lower() != 'mercado':
                                if userNameCompra not in resumen_usuarios:
                                    resumen_usuarios[userNameCompra] = {"username": userNameCompra, "compras": 0, "ventas": 0, "penalizaciones": 0}
                                resumen_usuarios[userNameCompra]["compras"] += valor
                except Exception as e:
                    print(f"   ⚠️ Excepcion en FICHAJES: {e}")
            elif cardName == 'CLÁUSULAS':
                try:
                    content_transfer_div = post.find_element(By.CSS_SELECTOR, "div.content.transfer")
                    jugadores_transferidos = content_transfer_div.find_elements(By.TAG_NAME, 'li')
                    for jugador in jugadores_transferidos:
                        userNames = get_user_name_clausulas(post)
                        userNameVenta = userNames[0]
                        userNameCompra = userNames[1]
                        valorVentaStr = jugador.find_element(By.TAG_NAME, 'strong').text.strip()
                        valor_limpio = valorVentaStr.replace('.', '').replace('€', '').replace(' ', '')
                        valor = int(valor_limpio)

                        if userNameVenta not in resumen_usuarios:
                            resumen_usuarios[userNameVenta] = {"username": userNameVenta, "compras": 0, "ventas": 0, "penalizaciones": 0}
                        resumen_usuarios[userNameVenta]["ventas"] += valor
                        if userNameCompra not in resumen_usuarios:
                            resumen_usuarios[userNameCompra] = {"username": userNameCompra, "compras": 0, "ventas": 0, "penalizaciones": 0}
                        resumen_usuarios[userNameCompra]["compras"] += valor

                except Exception as e:
                    print(f"   ⚠️ Excepcion en FICHAJES: {e}")

            elif cardName == 'ABONOS Y PENALIZACIONES':
                try:
                    content_bonus_div = post.find_element(By.CSS_SELECTOR, "div.content.bonus")
                    penalizaciones = content_bonus_div.find_elements(By.TAG_NAME, 'tr')
                    for penalizacion in penalizaciones:
                        userlink = penalizacion.find_element(By.TAG_NAME, 'user-link')
                        userName = userlink.find_element(By.TAG_NAME, 'a').text.strip()
                        decrement = post.find_element(By.CSS_SELECTOR, "increment.decrement.icon.icon-decrement").text.strip()
                        valor_limpio = decrement.replace('.', '').replace('€', '').replace(' ', '')
                        valor = int(valor_limpio)
                        if userName not in resumen_usuarios:
                            resumen_usuarios[userName] = {"username": userName, "compras": 0, "ventas": 0, "penalizaciones": 0}
                        resumen_usuarios[userName]["penalizaciones"] += valor
                except Exception as e:
                    print(f"   ⚠️ Excepcion en FICHAJES: {e}")

        except Exception as e:
            print(f"   ⚠️ No se pudo procesar post {i}: {e}")

    return list(resumen_usuarios.values())

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
        print(f"   ⚠️ Excepcion en get_user_name_fichajes: {e}")
    return userNames

def get_user_name_clausulas(post):
    try:
        userNames = []
        content_transfer_div = post.find_element(By.CSS_SELECTOR, "div.content.transfer")
        jugadores_transferidos = content_transfer_div.find_elements(By.TAG_NAME, 'li')
        for jugador in jugadores_transferidos:
            from_to_div = jugador.find_element(By.CSS_SELECTOR, "div.from-to")
            userlinks = from_to_div.find_elements(By.TAG_NAME, 'user-link')
            userNameVenta = userlinks[0].find_element(By.TAG_NAME, 'a').text.strip()
            userNameCompra = userlinks[1].find_element(By.TAG_NAME, 'a').text.strip()
            userNames.append(userNameVenta)
            userNames.append(userNameCompra)
    except Exception as e:
        print(f"   ⚠️ Excepcion en get_user_name_clausulas: {e}")
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
