from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from config import CARPETA_LOGS, CHROMEDRIVER_PATH
from datetime import datetime

# Variable global del módulo
_LOG_FILE_PATH = None

def ensure_directories_exist():
    CARPETA_LOGS.mkdir(parents=True, exist_ok=True)

def iniciar_log():
    """Crea el archivo de log único y escribe la línea de inicio."""
    global _LOG_FILE_PATH
    ensure_directories_exist()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    _LOG_FILE_PATH = CARPETA_LOGS / f"Biwenger_log_{timestamp}.log"
    with open(_LOG_FILE_PATH, "w", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] === Inicio ejecución script Biwenger ===\n")
    return _LOG_FILE_PATH

def log_message(message):
    """Escribe un mensaje en el log global y lo imprime en pantalla."""
    if _LOG_FILE_PATH is None:
        raise RuntimeError("El log no ha sido iniciado. Llama a iniciar_log() primero.")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}\n"

    with open(_LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(line)

def log_message_with_print(message):
    """Escribe un mensaje en el log global y lo imprime en pantalla."""
    if _LOG_FILE_PATH is None:
        raise RuntimeError("El log no ha sido iniciado. Llama a iniciar_log() primero.")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}\n"
    print(line.strip())
    with open(_LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(line)

def crear_driver():
    options = Options()
    options.add_argument("--start-maximized")

    try:
        log_message_with_print("🟡 Iniciando Chrome con perfil de usuario...")
        if not Path(CHROMEDRIVER_PATH).exists():
            raise FileNotFoundError(f"❌ Chromedriver no encontrado en {CHROMEDRIVER_PATH}")
        driver = webdriver.Chrome(options=options)
        log_message_with_print("🟢 Chrome iniciado correctamente.")
        return driver
    except Exception as e:
        log_message_with_print(f"❌ Error al crear el driver de Chrome: {e}")
        raise e

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
        log_message(f"ID: {usuario[0]}, Nombre: {usuario[1]}, Saldo: {usuario[2]}, URL Name: {usuario[3]}, Jugadores: {usuario[4]}, Fecha: {usuario[5]}")
