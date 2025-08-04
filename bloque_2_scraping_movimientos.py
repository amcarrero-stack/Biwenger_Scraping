from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from config import URL_BIWENGER_HOME, NOMBRE_MI_EQUIPO
from utils import log_message
import re

def parse_fecha_dom(title_str):
    """
    Convierte string tipo '2 ago 2025, 10:02:51' a datetime
    """
    meses = {
        "ene":1, "feb":2, "mar":3, "abr":4, "may":5, "jun":6,
        "jul":7, "ago":8, "sep":9, "oct":10, "nov":11, "dic":12
    }
    try:
        # Ejemplo título: '2 ago 2025, 10:02:51'
        dia, mes_str, anio_hora = title_str.split(" ", 2)
        mes = meses[mes_str.lower()]
        anio, hora = anio_hora.split(", ")
        fecha_dt = datetime.strptime(f"{dia}-{mes}-{anio} {hora}", "%d-%m-%Y %H:%M:%S")
        return fecha_dt
    except Exception as e:
        log_message(f"Error parseando fecha DOM: {title_str} -> {e}")
        return None

def extraer_movimientos(driver, fecha_ultima_ejecucion):
    """
    Extrae movimientos de fichajes y ventas desde la pestaña Inicio,
    considerando solo los ocurridos desde fecha_ultima_ejecucion.
    Devuelve diccionario {usuario: diferencia_saldo}.
    """

    saldo_movimientos = {}

    # Esperar y asegurarse que estamos en pestaña Inicio
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "league-board-post")))

    posts = driver.find_elements(By.TAG_NAME, "league-board-post")
    for post in posts:
        try:
            h3 = post.find_element(By.TAG_NAME, "h3").text.strip()
            title_div = post.find_element(By.CSS_SELECTOR, "div[title]")
            fecha_post = parse_fecha_dom(title_div.get_attribute("title"))
            if fecha_post is None:
                continue
            if fecha_post < fecha_ultima_ejecucion:
                # Es anterior a la última ejecución, ignoramos
                continue

            if "Mercado de fichajes" in h3:
                # Aquí restamos dinero (fichajes)
                transfer_list = post.find_element(By.TAG_NAME, "transfer-list")
                movimientos = transfer_list.find_elements(By.CSS_SELECTOR, "div[title]")
                for mov in movimientos:
                    title_text = mov.get_attribute("title")
                    # Ejemplo: 'Cambia por 9.930.000 € a Al-khelaifi'
                    m = re.search(r'Cambia por ([0-9\.\,]+) € a (.+)', title_text)
                    if m:
                        cantidad_str, usuario = m.groups()
                        cantidad = int(cantidad_str.replace(".", "").replace(",", ""))
                        if usuario == NOMBRE_MI_EQUIPO:
                            continue
                        saldo_movimientos[usuario] = saldo_movimientos.get(usuario, 0) - cantidad

            elif "Fichajes" in h3:
                # Aquí sumamos dinero (ventas)
                transfer_list = post.find_element(By.TAG_NAME, "transfer-list")
                movimientos = transfer_list.find_elements(By.CSS_SELECTOR, "div[title]")
                for mov in movimientos:
                    title_text = mov.get_attribute("title")
                    # Ejemplo: 'Vendido por Juanjo a Mercado por 1.800.300 €'
                    m = re.search(r'Vendido por (.+) a Mercado por ([0-9\.\,]+) €', title_text)
                    if m:
                        usuario, cantidad_str = m.groups()
                        cantidad = int(cantidad_str.replace(".", "").replace(",", ""))
                        if usuario == NOMBRE_MI_EQUIPO:
                            continue
                        saldo_movimientos[usuario] = saldo_movimientos.get(usuario, 0) + cantidad

        except Exception as e:
            log_message(f"Error procesando un post: {e}")
            continue

    return saldo_movimientos
