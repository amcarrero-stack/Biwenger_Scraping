from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from config import CARPETA_LOGS, CHROMEDRIVER_PATH
from datetime import datetime

def crear_driver(logFilePath):
    options = Options()
    options.add_argument("--start-maximized")

    try:
        log_message(logFilePath, "🟡 Iniciando Chrome con perfil de usuario...")

        if not Path(CHROMEDRIVER_PATH).exists():
            raise FileNotFoundError(f"❌ Chromedriver no encontrado en {CHROMEDRIVER_PATH}")

        driver = webdriver.Chrome(options=options)
        # driver = webdriver.Chrome()

        log_message(logFilePath, "🟢 Chrome iniciado correctamente.")
        return driver
    except Exception as e:
        log_message(logFilePath, f"❌ Error al crear el driver de Chrome: {e}")
        raise e
def ensure_directories_exist():
    for carpeta in [CARPETA_LOGS]:
        carpeta.mkdir(parents=True, exist_ok=True)

def iniciar_log():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logFilePath = CARPETA_LOGS / f"Biwenger_log_{timestamp}.log"
    return logFilePath

def log_message(logFilePath, message):
    if logFilePath is None:
        raise RuntimeError("El log no ha sido iniciado. Llama a iniciar_log() primero.")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}\n"
    print(line.strip())
    with open(logFilePath, "a", encoding="utf-8") as f:
        f.write(line)

def obtener_timestamp_actual(formato="%Y-%m-%d_%H-%M-%S"):
    return datetime.now().strftime(formato)

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