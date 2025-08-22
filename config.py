from pathlib import Path

# === RUTAS PRINCIPALES ===
CARPETA_BASE = Path(__file__).parent
CARPETA_LOGS = CARPETA_BASE / "logs"

# === FORMATOS FECHAS ===
FORMATO_TIMESTAMP_ARCHIVOS = "%Y%m%d_%H%M%S"  # Para nombres de archivos (logs, html)
PATRON_FECHA_DOM = "%d %b %Y, %H:%M:%S"  # Para fechas en DOM Biwenger

# Ruta al ejecutable del chromedriver (ajusta si lo has movido)
CHROMEDRIVER_PATH = r"C:\Users\Tito\Desktop\Biwenger_Scraping\chromedriver.exe"

def LOG_FILE(timestamp=None):
    if timestamp is None:
        from datetime import datetime
        timestamp = datetime.now().strftime(FORMATO_TIMESTAMP_ARCHIVOS)
    return CARPETA_LOGS / f"Biwenger_log_{timestamp}.log"


# === CONFIGURACIONES DE INICIALIZACIÓN ===
SALDO_INICIAL = 20_000_000  # 20 millones
FECHA_INICIO_LIGA = "2025-08-01"

# === URLS BIWENGER ===
URL_BIWENGER_HOME = "https://biwenger.as.com/"
URL_BIWENGER_EQUIPO = "https://biwenger.as.com/team"
URL_BIWENGER_LIGA = "https://biwenger.as.com/league"
URL_BIWENGER_PLAYERS = "https://biwenger.as.com/players"

# === SELENIUM ===
CHROME_DRIVER_PATH = None  # Usar el ChromeDriver que tenga el sistema por defecto
TIEMPO_ESPERA_CARGA = 10  # segundos
