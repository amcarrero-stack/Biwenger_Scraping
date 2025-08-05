import time
from datetime import datetime, timedelta

from config import URL_BIWENGER_HOME, NOMBRE_MI_EQUIPO, URL_BIWENGER_LIGA
from utils import log_message, crear_driver, get_posts_until_date, mostrar_texto_h3, traducir_mes
from bloque_1_inicializacion import inicializar_bbdd_y_directorios
from bloque_2_scraping_movimientos import extraer_movimientos
from bloque_3_scraping_plantillas import obtener_usuarios, extraer_plantilla_usuario
from bloque_4_excel_update import cargar_o_crear_excel, actualizar_datos_excel
from bloque_5_generar_html import generar_html
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def main():
    log_message("=== Inicio ejecución script Biwenger ===")

    try:
        inicializar_bbdd_y_directorios()
        driver = crear_driver()

        # Abrimos directamente la home
        log_message("🌐 Navegando a la página principal de Biwenger...")
        driver.get("https://biwenger.as.com/")
        time.sleep(3)  # Esperar a que cargue del todo
        web_element_agree = driver.find_elements(By.ID, 'didomi-notice-agree-button')[0]
        web_element_agree.click()

        web_element_comienzo = driver.find_elements(By.CSS_SELECTOR, 'a.btn.primary.xl[href="/login"]')[0]
        web_element_comienzo.click()

        web_element_cuentaDisponible = driver.find_elements(By.LINK_TEXT, "Ya tengo cuenta")[0]
        web_element_cuentaDisponible.click()

        web_element_email_input = driver.find_elements(By.NAME, 'email')[0]
        web_element_email_input.send_keys("amcarrero@gmail.com")

        web_element_email_input = driver.find_elements(By.NAME, 'password')[0]
        web_element_email_input.send_keys("Carrero1110")
        time.sleep(3)

        web_element_boton_login = driver.find_elements(By.CSS_SELECTOR, 'button.btn.squared')[0]
        web_element_boton_login.click()

        input("🔒 Inicia sesión (si no lo estás) y pulsa Enter para continuar...")
        time.sleep(1)
        driver.get(URL_BIWENGER_LIGA)
        time.sleep(1)
        usuarios = obtener_usuarios(driver)

        nombres_usuarios = [u[0] for u in usuarios]
        log_message(f"Usuarios detectados (excluyendo {NOMBRE_MI_EQUIPO}): {nombres_usuarios}")

        driver.get(URL_BIWENGER_HOME)
        fecha_str = '29 jul 2025'
        fecha_str_traducida = traducir_mes(fecha_str)
        cutoff_datetime = datetime.strptime(fecha_str_traducida, "%d %b %Y")
        posts = get_posts_until_date(driver, cutoff_datetime)
        print(f"Se han recogido {len(posts)} movimientos hasta {fecha_str}")

        mostrar_texto_h3(posts)
        #
        # df = cargar_o_crear_excel(nombres_usuarios)
        # ultima_fecha_str = df["Fecha/Hora"].dropna().max()
        # if ultima_fecha_str:
        #     fecha_ultima_ejecucion = datetime.strptime(ultima_fecha_str, "%Y-%m-%d %H:%M:%S")
        # else:
        #     fecha_ultima_ejecucion = datetime(2025, 8, 1, 0, 0, 0)
        # log_message(f"Fecha última ejecución: {fecha_ultima_ejecucion}")
        #
        # driver.get(URL_BIWENGER_HOME)
        # time.sleep(5)
        # movimientos = extraer_movimientos(driver, fecha_ultima_ejecucion)
        # log_message(f"Movimientos detectados: {movimientos}")
        #
        # plantilla_por_usuario = {}
        # for usuario, url in usuarios:
        #     plantilla, total_jugadores = extraer_plantilla_usuario(driver, url)
        #     plantilla_por_usuario[usuario] = plantilla
        #     log_message(f"Plantilla extraída para {usuario}: {total_jugadores} jugadores")
        #
        # df_actualizado = actualizar_datos_excel(df, movimientos, plantilla_por_usuario)
        # saldos = {row["Nombre"]: row["Saldo"] for _, row in df_actualizado.iterrows()}
        # generar_html(plantilla_por_usuario, saldos)
        # log_message("✅ Script ejecutado con éxito.")

    except Exception as e:
        log_message(f"❌ Error durante la ejecución: {e}")

    finally:
        if 'driver' in locals():
            driver.quit()
        log_message("=== Fin ejecución script Biwenger ===")

if __name__ == "__main__":
    main()