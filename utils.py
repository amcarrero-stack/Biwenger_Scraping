from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from config import CARPETA_BBDD, CARPETA_RESULTADOS, CARPETA_LOGS, LOG_FILE, HTML_FILE, EXCEL_BBDD
from datetime import datetime, date

CHROMEDRIVER_PATH = r"C:\Users\Tito\Desktop\Biwenger_Scraping\chromedriver.exe"
CHROME_PROFILE_PATH = r"C:\Users\Tito\AppData\Local\Google\Chrome\User Data"
CHROME_PROFILE_NAME = "Default"

def crear_driver():
    #chromedriver_autoinstaller.install()

    options = Options()
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

def traducir_mes(mes_es):
    traducciones = {
        "ene": "Jan", "feb": "Feb", "mar": "Mar", "abr": "Apr",
        "may": "May", "jun": "Jun", "jul": "Jul", "ago": "Aug",
        "sep": "Sep", "oct": "Oct", "nov": "Nov", "dic": "Dec"
    }
    for esp, eng in traducciones.items():
        mes_es = mes_es.replace(f" {esp} ", f" {eng} ")
    return mes_es

def print_usuarios(usuarios):
    for usuario in usuarios:
        print(f"ID: {usuario[0]}, Nombre: {usuario[1]}, Saldo: {usuario[2]}, URL Name: {usuario[3]}, Jugadores: {usuario[4]}, Fecha: {usuario[5]}")