import time
import os
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
from config import CARPETA_BBDD, CARPETA_RESULTADOS, CARPETA_LOGS, LOG_FILE, HTML_FILE, EXCEL_BBDD
from selenium.webdriver.common.by import By
from datetime import datetime

CHROMEDRIVER_PATH = r"C:\Users\Tito\Desktop\Biwenger_Scraping\chromedriver.exe"
CHROME_PROFILE_PATH = r"C:\Users\Tito\AppData\Local\Google\Chrome\User Data"
CHROME_PROFILE_NAME = "Default"

def crear_driver():
    #chromedriver_autoinstaller.install()

    options = Options()
    # options.add_argument(f"--user-data-dir={CHROME_PROFILE_PATH}")
    # options.add_argument(f"--profile-directory={CHROME_PROFILE_NAME}")
    # options.add_argument("--start-maximized")
    # options.add_argument("--disable-extensions")
    # options.add_argument("--disable-gpu")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    # options.add_experimental_option("detach", True)
    options.add_argument("--start-maximized")
    try:
        log_message("🟡 Iniciando Chrome con perfil de usuario...")

        if not Path(CHROMEDRIVER_PATH).exists():
            raise FileNotFoundError(f"❌ Chromedriver no encontrado en {CHROMEDRIVER_PATH}")

        driver = webdriver.Chrome(options=options)
        # driver = webdriver.Chrome()

        log_message("🟢 Chrome iniciado correctamente.")
        return driver
    except Exception as e:
        log_message(f"❌ Error al crear el driver de Chrome: {e}")
        raise e
def ensure_directories_exist():
    for carpeta in [CARPETA_BBDD, CARPETA_RESULTADOS, CARPETA_LOGS]:
        carpeta.mkdir(parents=True, exist_ok=True)

def get_excel_path():
    return EXCEL_BBDD

def log_message(message):
    ensure_directories_exist()
    timestamp_file = obtener_timestamp_actual("%Y-%m-%d_%H-%M-%S")
    log_file = LOG_FILE(timestamp_file)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}\n"
    print(line.strip())
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line)

def get_html_path():
    timestamp_file = obtener_timestamp_actual("%Y-%m-%d_%H-%M-%S")
    return HTML_FILE(timestamp_file)

def obtener_timestamp_actual(formato="%Y-%m-%d_%H-%M-%S"):
    return datetime.now().strftime(formato)

def formatear_fecha_biwenger(fecha_str):
    from datetime import datetime
    import locale
    try:
        locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
    except:
        locale.setlocale(locale.LC_TIME, "es_ES")
    try:
        return datetime.strptime(fecha_str, "%d %b %Y, %H:%M:%S")
    except Exception as e:
        log_message(f"Error al parsear fecha '{fecha_str}': {e}")
        return None
def get_posts_until_date(driver, cutoff_datetime):
    print('entra en get_posts_until_date')
    last_height = driver.execute_script("return document.body.scrollHeight")
    postToOld = []
    while True:
        time.sleep(1)
        all_posts = driver.find_elements(By.CSS_SELECTOR, 'league-board-post')
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

                if not is_a_valid_post:
                    continue
                elif post_datetime >= cutoff_datetime:
                    postToRet.append(post)
                else:
                    return postToRet

            except Exception:
                continue

        # Hacemos scroll para cargar más posts
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # Ya no hay más contenido para cargar
            break
        last_height = new_height
    return postToOld

def check_league_board_post(league_board_post):
    try:
        header_div = league_board_post.find_element(By.CSS_SELECTOR, "div.header.ng-star-inserted")
        h3_element = header_div.find_element(By.TAG_NAME, "h3")
        cardName = h3_element.text.strip()
        return cardName == 'MERCADO DE FICHAJES' or cardName == 'FICHAJES' or cardName == 'CAMBIO DE NOMBRE'
    except Exception as e:
        print(f"   ⚠️ No se pudo encontrar el h3 esperado: {e}")

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
    for i, post in enumerate(posts, start=1):
        try:
            header_div = post.find_element(By.CSS_SELECTOR, "div.header.ng-star-inserted")
            h3_element = header_div.find_element(By.TAG_NAME, "h3")
            date_elem = header_div.find_element(By.CSS_SELECTOR, "div.date")
            date_str = date_elem.get_attribute("title").split(',')[0]

            cardName = h3_element.text.strip()
            if cardName == 'MERCADO DE FICHAJES':
                print(f"\n📌 Post {i}:")
                print(f"   - {h3_element.text.strip()} ({date_str})")
                merc_fichajes_div = post.find_element(By.CSS_SELECTOR, "div.content.market")
                fichajes = merc_fichajes_div.find_elements(By.TAG_NAME, 'li')
                for fichaje in fichajes:
                    fichajeH3 = fichaje.find_element(By.TAG_NAME, "h3")
                    fichajeName = fichajeH3.text.strip()
                    print(f"      - {fichajeName}")

            # elif cardName == 'FICHAJES':
            #     print(f"\n📌 Post {i}:")
            #     print(f"   - {h3_element.text.strip()}")



        except Exception as e:
            print(f"   ⚠️ No se pudo encontrar el h3 esperado: {e}")