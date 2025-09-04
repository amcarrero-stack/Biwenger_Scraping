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
        header_div = post.find_element(By.CSS_SELECTOR, "div.header")
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
        header_div = post.find_element(By.CSS_SELECTOR, "div.header")
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
        header_div = post.find_element(By.CSS_SELECTOR, "div.header")
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
        time_relatives = post.find_elements(By.CSS_SELECTOR, "time-relative")
        post_datetime = datetime.today().replace(microsecond=0)
        if time_relatives:
            fecha_sin_formato = time_relatives[0].get_attribute("title")
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

class Penalizacion:
    def __init__(self, nombre_jugador, accion):
        self.nombre_jugador = nombre_jugador
        self.accion = accion
    def __repr__(self):
        return f"<nombre de jugador={self.nombre_jugador}, accion realizada={self.accion} >"
class Penalizaciones:
    def __init__(self, post):
        header_div = post.find_element(By.CSS_SELECTOR, "div.header")
        date_elem = header_div.find_element(By.CSS_SELECTOR, "div.date")
        date_str = date_elem.get_attribute("title")
        post_datetime = traducir_mes(date_str)
        self.fecha = post_datetime
        self.penalizaciones = self._parse_penalizaciones(post)
    def _parse_penalizaciones(self, post):
        penalizaciones_list = []
        try:
            content_bonus_div = post.find_element(By.CSS_SELECTOR, "div.content.bonus")
            penalizaciones = content_bonus_div.find_elements(By.TAG_NAME, 'tr')
            for penalizacion in penalizaciones:
                userlink = penalizacion.find_element(By.TAG_NAME, 'user-link')
                user_name = userlink.find_element(By.TAG_NAME, 'a').text.strip()
                decrement = penalizacion.find_element(By.CSS_SELECTOR, "increment.decrement.icon.icon-decrement").text.strip()
                valor = decrement.replace('.', '').replace('€', '').replace(' ', '')
                penalizaciones_list.append(Penalizacion('Penalizador', user_name + ' es penalizado con ' + valor))
        except Exception as e:
            log_message(f"   ⚠️ Excepcion en parse penalizaciones: {e}")
        return penalizaciones_list
    def __repr__(self):
        return f"<fecha={self.fecha}, fichajes={self.penalizaciones}>"

class Movimiento:
    def __init__(self, nombre_jugador, accion):
        self.nombre_jugador = nombre_jugador
        self.accion = accion
    def __repr__(self):
        return f"<nombre de jugador={self.nombre_jugador}, accion realizada={self.accion} >"
class Movimientos:
    def __init__(self, post):
        header_div = post.find_element(By.CSS_SELECTOR, "div.header")
        date_elem = header_div.find_element(By.CSS_SELECTOR, "div.date")
        date_str = date_elem.get_attribute("title")
        post_datetime = traducir_mes(date_str)
        self.fecha = post_datetime
        self.movimientos = self._parse_movimientos(post)
    def _parse_movimientos(self, post):
        movimientos_list = []
        player_movements_div = post.find_element(By.CSS_SELECTOR, "div.content.playerMovements")
        players = player_movements_div.find_elements(By.TAG_NAME, 'li')
        for player in players:
            player_name = player.find_element(By.CSS_SELECTOR, "div.main h3 a").text.strip()
            team_link_list = player.find_elements(By.CSS_SELECTOR, "div.content team-link")
            accion = ''
            if len(team_link_list) == 0:
                accion = ' ha abandonado la competicion'
            elif len(team_link_list) == 1:
                team_link = team_link_list[0]
                a_tag = team_link.find_element(By.TAG_NAME, "a")
                title = a_tag.get_attribute("title")
                accion = ' fichado por ' + title
            elif len(team_link_list) == 2:
                team_link = team_link_list[0]
                a_tag = team_link.find_element(By.TAG_NAME, "a")
                equipo1 = a_tag.get_attribute("title")
                team_link2 = team_link_list[1]
                a_tag_2 = team_link2.find_element(By.TAG_NAME, "a")
                equipo2 = a_tag_2.get_attribute("title")
                accion = ' transferido de ' + equipo1 + ' a ' + equipo2

            if accion:
                movimientos_list.append(Movimiento(player_name, accion))
        return movimientos_list
    def __repr__(self):
        return f"<fecha={self.fecha}, fichajes={self.movimientos_list}>"

class Post:
    def __init__(self, post):
        try:
            header_div = post.find_element(By.CSS_SELECTOR, "div.header")
            h3_element = header_div.find_element(By.TAG_NAME, "h3")
            cardName = h3_element.text.strip()
            if cardName == 'FICHAJES':
                self.post_returned = Ventas(post)
            elif cardName == 'MERCADO DE FICHAJES':
                self.post_returned = Fichajes(post)
            elif cardName == 'CLÁUSULAS':
                self.post_returned = Clausulazos(post)
            elif cardName == 'ABONOS Y PENALIZACIONES':
                self.post_returned = Penalizaciones(post)
                print(cardName)
            elif cardName == 'CAMBIO DE NOMBRE':
                # post = Ventas(post)
                print(cardName)
            elif cardName == 'MOVIMIENTO DE JUGADORES':
                self.post_returned = Movimientos(post)
        except Exception as e:
            error_message = e.__str__()
            patron = r'(\{"method":".*?"\})'
            coincidencia = re.search(patron, error_message)

            if coincidencia:
                json_str_obj = json.loads(coincidencia.group(1))
                if json_str_obj['method'] == 'css selector' and json_str_obj['selector'] == 'div.header' and check_tag_exit(post, "div.panel-header h3") and "Fin de" in post.find_element(By.CSS_SELECTOR, "div.panel-header h3").text.strip():
                    self.post_returned = Abonos(post)
    def __repr__(self):
        return f"<post_returned={self.post_returned}>"