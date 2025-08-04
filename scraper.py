from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from config import CHROME_DRIVER_PATH, BIWENGER_HOME_URL
from utils import log_message

def iniciar_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def login_biwenger(driver):
    driver.get(BIWENGER_HOME_URL)
    log_message("Navegador abierto en Biwenger.")
    input("Inicia sesión manualmente con tu cuenta de Google y pulsa ENTER para continuar...")
    log_message("Inicio de sesión completado (manual).")

def navegar_a(driver, tab_name: str):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        tabs = driver.find_elements(By.TAG_NAME, "a")
        for tab in tabs:
            if tab_name.lower() in tab.text.lower():
                tab.click()
                time.sleep(3)
                log_message(f"Navegado a la pestaña: {tab_name}")
                return
        log_message(f"No se encontró la pestaña '{tab_name}'.")
    except Exception as e:
        log_message(f"Error al navegar a '{tab_name}': {str(e)}")

def obtener_html(driver):
    return driver.page_source

def cerrar_driver(driver):
    driver.quit()
    log_message("Driver cerrado correctamente.")
