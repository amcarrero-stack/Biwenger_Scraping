from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from utils import log_message
from config import NOMBRE_MI_EQUIPO
import time

# def obtener_usuarios(driver):
#     """
#     En la pestaña Liga, extrae enlaces y nombres de usuarios (excluye tu usuario).
#     Devuelve lista de tuples (nombre_usuario, url_usuario).
#     """
#     usuarios = []
#     WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[role='button'][aria-haspopup='dialog']")))
#     enlaces = driver.find_elements(By.CSS_SELECTOR, "a[role='button'][aria-haspopup='dialog']")
#     for a in enlaces:
#         nombre = a.text.strip()
#         href = a.get_attribute("href")
#         if nombre != NOMBRE_MI_EQUIPO:
#             usuarios.append((nombre, href))
#     return usuarios
def obtener_usuarios(driver):
    usuarios = []
    cards = driver.find_elements(By.CSS_SELECTOR, "user-card")
    for card in cards:
        try:
            # Dentro de cada card, busca el <h3><a> con el nombre de usuario
            enlace = card.find_element(By.CSS_SELECTOR, "div.main h3 a")
            nombre = enlace.text.strip()
            href = enlace.get_attribute("href")

            if nombre != NOMBRE_MI_EQUIPO:
                usuarios.append((nombre, href))
        except:
            continue  # Por si algún user-card no tiene nombre o el selector falla
    print(usuarios)
    return usuarios
def extraer_plantilla_usuario(driver, url_usuario):
    """
    Accede a la URL de un usuario y extrae plantilla por posición.
    Devuelve dict: {posicion: [jugadores]} con posiciones: Porteros, Defensas, Centrocampistas, Delanteros.
    También devuelve el número total de jugadores.
    """
    plantilla = {
        "Porteros": [],
        "Defensas": [],
        "Centrocampistas": [],
        "Delanteros": []
    }

    driver.get(url_usuario)
    time.sleep(2)  # Espera a que cargue la página

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h4[text()='Plantilla']"))
        )
    except:
        log_message(f"No se encontró la sección 'Plantilla' en {url_usuario}")
        return plantilla, 0

    # Localizamos la sección 'Plantilla'
    contenedor = driver.find_element(By.XPATH, "//h4[text()='Plantilla']/following-sibling::div")

    # Cada posición suele estar dentro de un div con título
    posiciones_map = {
        "Porteros": ["Portero", "Porteros"],
        "Defensas": ["Defensa", "Defensas"],
        "Centrocampistas": ["Centrocampista", "Centrocampistas", "Mediocentro", "Mediocentros", "Medio"],
        "Delanteros": ["Delantero", "Delanteros", "Atacante", "Atacantes"]
    }

    # Extraer todos los bloques de posición (títulos y jugadores)
    bloques = contenedor.find_elements(By.XPATH, "./div")

    for bloque in bloques:
        try:
            titulo = bloque.find_element(By.TAG_NAME, "strong").text.strip()
            jugadores = bloque.find_elements(By.TAG_NAME, "span")
            lista_jugadores = [j.text.strip() for j in jugadores if j.text.strip() != ""]

            # Asignar a la posición correcta
            for pos_clave, lista_alias in posiciones_map.items():
                if titulo in lista_alias:
                    plantilla[pos_clave].extend(lista_jugadores)
                    break
        except Exception as e:
            log_message(f"Error extrayendo plantilla en bloque: {e}")
            continue

    # Contar total jugadores
    total_jugadores = sum(len(v) for v in plantilla.values())

    return plantilla, total_jugadores
