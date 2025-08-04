import shutil
import tempfile
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller
from config import CHROMEDRIVER_PATH, CARPETA_BBDD, CARPETA_RESULTADOS, CARPETA_LOGS, LOG_FILE, HTML_FILE, EXCEL_BBDD, CHROME_PROFILE_PATH, CHROME_PROFILE_NAME

def crear_driver():
    chromedriver_autoinstaller.install()

    options = Options()

    # 🧪 Copiar perfil real a uno temporal para evitar errores de sesión
    temp_profile = tempfile.mkdtemp()
    original_profile_path = f"{CHROME_PROFILE_PATH}\\{CHROME_PROFILE_NAME}"
    try:
        shutil.copytree(original_profile_path, f"{temp_profile}\\Default", dirs_exist_ok=True)
    except Exception as e:
        log_message(f"⚠️ No se pudo copiar perfil original: {e}")

    options.add_argument(f"--user-data-dir={temp_profile}")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("detach", True)

    try:
        log_message("🟡 Iniciando Chrome con perfil clonado (temporal)...")
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        log_message("🟢 Chrome iniciado correctamente.")
        return driver
    except Exception as e:
        log_message(f"❌ Error al crear el driver de Chrome: {e}")
        raise e
