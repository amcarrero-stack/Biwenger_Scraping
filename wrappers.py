from selenium.webdriver.common.by import By
from utils import *
from bloque_1_selenium import *
from bloque_bbdd import *
class Venta:
    def __init__(self, nombre_jugador, accion):
        self.nombre_jugador = nombre_jugador
        self.accion = accion

    def __repr__(self):
        return f"<nombre de jugador={self.nombre_jugador}, accion realizada={self.accion} >"
class Ventas:
    def __init__(self, post):
        header_div = post.find_element(By.CSS_SELECTOR, "div.header.ng-star-inserted")
        date_elem = header_div.find_element(By.CSS_SELECTOR, "div.date")
        date_str = date_elem.get_attribute("title")
        post_datetime = traducir_mes(date_str)
        self.fecha = post_datetime
        self.ventas = self._parse_ventas(post)

    def _parse_ventas(self, post):
        ventas = []
        try:
            content_transfer_div = post.find_element(By.CSS_SELECTOR, "div.content.transfer")
            jugadores_transferidos = content_transfer_div.find_elements(By.TAG_NAME, 'li')
            for jugador in jugadores_transferidos:
                jugadorName = jugador.find_element(By.CSS_SELECTOR, "div.main h3 a").text.strip()
                accion_div = jugador.find_element(By.CSS_SELECTOR, "player-card div.content div[title]")
                accion = accion_div.get_attribute("title")
                ventas.append(Venta(jugadorName, accion))
        except Exception as e:
            log_message(f"   ⚠️ Excepcion en parse ventas: {e}")
        return ventas
    def __repr__(self):
        return f"<fecha={self.fecha}, fichajes={self.ventas}>"

class Fichaje:
    def __init__(self, nombre_jugador, accion):
        self.nombre_jugador = nombre_jugador
        self.accion = accion
    def __repr__(self):
        return f"<nombre de jugador={self.nombre_jugador}, accion realizada={self.accion} >"
class Fichajes:
    def __init__(self, post):
        header_div = post.find_element(By.CSS_SELECTOR, "div.header.ng-star-inserted")
        date_elem = header_div.find_element(By.CSS_SELECTOR, "div.date")
        date_str = date_elem.get_attribute("title")
        post_datetime = traducir_mes(date_str)
        self.fecha = post_datetime
        self.fichajes = self._parse_fichajes(post)
    def _parse_fichajes(self, post):
        fichajes = []
        try:
            content_transfer_div = post.find_element(By.CSS_SELECTOR, "div.content.market")
            jugadores_transferidos = content_transfer_div.find_elements(By.TAG_NAME, 'li')
            for jugador in jugadores_transferidos:
                jugadorName = jugador.find_element(By.CSS_SELECTOR, "div.main h3 a").text.strip()
                accion_div = jugador.find_element(By.CSS_SELECTOR, "player-card div.content div[title]")
                accion = accion_div.get_attribute("title")
                fichajes.append(Fichaje(jugadorName, accion))
        except Exception as e:
            log_message(f"   ⚠️ Excepcion en parse fichajes: {e}")
        return fichajes
    def __repr__(self):
        return f"<fecha={self.fecha}, fichajes={self.fichajes}>"

class Clausulazo:
    def __init__(self, nombre_jugador, accion):
        self.nombre_jugador = nombre_jugador
        self.accion = accion
    def __repr__(self):
        return f"<nombre de jugador={self.nombre_jugador}, accion realizada={self.accion} >"
class Clausulazos:
    def __init__(self, post):
        header_div = post.find_element(By.CSS_SELECTOR, "div.header.ng-star-inserted")
        date_elem = header_div.find_element(By.CSS_SELECTOR, "div.date")
        date_str = date_elem.get_attribute("title")
        post_datetime = traducir_mes(date_str)
        self.fecha = post_datetime
        self.clausulazos = self._parse_clausulazos(post)
    def _parse_clausulazos(self, post):
        clausulazos = []
        try:
            content_transfer_div = post.find_element(By.CSS_SELECTOR, "div.content.transfer")
            jugadores_transferidos = content_transfer_div.find_elements(By.TAG_NAME, 'li')
            for jugador in jugadores_transferidos:
                jugadorName = jugador.find_element(By.CSS_SELECTOR, "div.main h3 a").text.strip()
                accion_div = jugador.find_element(By.CSS_SELECTOR, "player-card div.content div[title]")
                accion = accion_div.get_attribute("title")
                clausulazos.append(Fichaje(jugadorName, accion))
        except Exception as e:
            log_message(f"   ⚠️ Excepcion en parse clausulazos: {e}")
        return clausulazos
    def __repr__(self):
        return f"<fecha={self.fecha}, fichajes={self.clausulazos}>"
class Abono:
    def __init__(self, nombre_jugador, accion):
        self.nombre_jugador = nombre_jugador
        self.accion = accion
    def __repr__(self):
        return f"<nombre de jugador={self.nombre_jugador}, accion realizada={self.accion} >"
class Abonos:
    def __init__(self, post):
        time_relative = post.find_element(By.CSS_SELECTOR, "time-relative")
        fecha_sin_formato = time_relative.get_attribute("title")
        post_datetime = datetime.strptime(fecha_sin_formato, "%d/%m/%y, %H:%M")
        self.fecha = post_datetime
        self.abonos = self._parse_abonos(post)
    def _parse_abonos(self, post):
        abonos = []
        try:
            card_h3 = post.find_element(By.CSS_SELECTOR, "h3")
            numero_de_jornada_text = card_h3.find_element(By.CSS_SELECTOR, "a").text.strip()
            tr_list = post.find_elements(By.CSS_SELECTOR, 'div.content tr')
            for row in tr_list:
                td_list = row.find_elements(By.CSS_SELECTOR, 'td')
                user_name = td_list[1].find_element(By.CSS_SELECTOR, "a").text.strip()
                valor = td_list[3].find_element(By.CSS_SELECTOR, "increment").text.replace(" €", "").replace(".", "")
                abonos.append(Abono(numero_de_jornada_text, user_name + ' obtiene '+ valor))
        except Exception as e:
            log_message(f"   ⚠️ Excepcion en parse abonos: {e}")
        return abonos
    def __repr__(self):
        return f"<fecha={self.fecha}, fichajes={self.abonos}>"

class Post:
    def __init__(self, post):
        try:
            header_div = post.find_element(By.CSS_SELECTOR, "div.header.ng-star-inserted")
            h3_element = header_div.find_element(By.TAG_NAME, "h3")
            cardName = h3_element.text.strip()
            post
            if cardName == 'FICHAJES':
                post = Ventas(post)
            elif cardName == 'MERCADO DE FICHAJES':
                post = Fichajes(post)
            elif cardName == 'CLÁUSULAS':
                post = Clausulazos(post)
            elif cardName == 'ABONOS Y PENALIZACIONES':
                # post = Ventas(post)
                print(cardName)
            elif cardName == 'CAMBIO DE NOMBRE':
                # post = Ventas(post)
                print(cardName)
            elif cardName == 'MOVIMIENTO DE JUGADORES':
                # post = Ventas(post)
                print(cardName)
            else:
                post = Abonos(post)

            self.post_returned = post
        except Exception as e:
            log_message(f"   ⚠️ No se pudo encontrar el h3 esperado: {e}")
    def __repr__(self):
        return f"<post_returned={self.post_returned}>"