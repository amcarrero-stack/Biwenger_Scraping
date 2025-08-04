from pathlib import Path

# === CONFIGURACIÓN GENERAL ===
NOMBRE_MI_EQUIPO = "Pierre Nodoyuna"  # NO se extraerá información de este equipo
NOMBRE_LIGA = "Liga Carlos Carrero"

# === RUTAS PRINCIPALES ===
ESCRITORIO = Path.home() / "Escritorio"
CARPETA_BASE = ESCRITORIO / "Biwenger_Info"
CARPETA_BBDD = CARPETA_BASE / "BBDD"
CARPETA_RESULTADOS = CARPETA_BASE / "Resultado"
CARPETA_LOGS = CARPETA_BASE / "LOGS"

# === FORMATOS FECHAS ===
FORMATO_TIMESTAMP_ARCHIVOS = "%Y%m%d_%H%M%S"  # Para nombres de archivos (logs, html)
PATRON_FECHA_DOM = "%d %b %Y, %H:%M:%S"  # Para fechas en DOM Biwenger

# === ARCHIVOS ===
EXCEL_BBDD = CARPETA_BBDD/"Biwenger_BBDD.xlsx"

# Ruta donde está instalado tu Chrome (perfil de usuario)
CHROME_PROFILE_PATH = r"C:\Users\Tito\AppData\Local\Google\Chrome\User Data"
CHROME_PROFILE_NAME = "Default"  # O "Profile 1" si tienes otro perfil

# Ruta al ejecutable del chromedriver (ajusta si lo has movido)
CHROMEDRIVER_PATH = r"C:\Users\Tito\Desktop\Biwenger_Scraping\chromedriver.exe"

def LOG_FILE(timestamp=None):
    if timestamp is None:
        from datetime import datetime
        timestamp = datetime.now().strftime(FORMATO_TIMESTAMP_ARCHIVOS)
    return CARPETA_LOGS / f"Biwenger_log_{timestamp}.log"

def HTML_FILE(timestamp=None):
    if timestamp is None:
        from datetime import datetime
        timestamp = datetime.now().strftime(FORMATO_TIMESTAMP_ARCHIVOS)
    return CARPETA_RESULTADOS / f"Biwenger_2025_26_{timestamp}.html"

# === CONFIGURACIONES DE INICIALIZACIÓN ===
SALDO_INICIAL = 20_000_000  # 20 millones
FECHA_INICIO_LIGA = "2025-08-01"

# === URLS BIWENGER ===
URL_BIWENGER_HOME = "https://biwenger.as.com/"
URL_BIWENGER_EQUIPO = "https://biwenger.as.com/team"
URL_BIWENGER_LIGA = "https://biwenger.as.com/league"

# === SELENIUM ===
CHROME_DRIVER_PATH = None  # Usar el ChromeDriver que tenga el sistema por defecto
TIEMPO_ESPERA_CARGA = 10  # segundos
