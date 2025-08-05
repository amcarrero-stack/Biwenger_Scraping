import time
from datetime import datetime, timedelta

from config import URL_BIWENGER_HOME, NOMBRE_MI_EQUIPO, URL_BIWENGER_LIGA
from utils import log_message, crear_driver
from bloque_1_selenium import get_posts_until_date, mostrar_texto_h3
from bloque_1_selenium import do_login, do_obtener_usuarios
from bloque_bbdd import get_db_connection, crear_tablas_si_no_existen, cerrar_BBDD, insertar_usuario, obtener_usuarios, print_usuarios
from bloque_2_scraping_movimientos import extraer_movimientos
from bloque_4_excel_update import cargar_o_crear_excel, actualizar_datos_excel
from bloque_5_generar_html import generar_html
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def main():
    log_message("=== Inicio ejecución script Biwenger ===")

    try:
        # inicializar_bbdd_y_directorios()
        conn = get_db_connection()
        crear_tablas_si_no_existen(conn)

        driver = crear_driver()
        log_message("🌐 Navegando a la página principal de Biwenger...")
        do_login(driver)
        # input("🔒 Inicia sesión (si no lo estás) y pulsa Enter para continuar...")
        usuarios_actuales = do_obtener_usuarios(driver)
        print(f"Usuarios detectados (excluyendo {NOMBRE_MI_EQUIPO}): {[u['name'] for u in usuarios_actuales]}")
        usuarios_db = obtener_usuarios(conn)
        if not usuarios_db:
            insertar_usuario(conn, usuarios_actuales)
            usuarios_db = obtener_usuarios(conn)
        modification_date = usuarios_db[0][5]
        print(f'modification_date es {modification_date}')
        print_usuarios(obtener_usuarios(conn))
        cerrar_BBDD(conn)
        posts = get_posts_until_date(driver, modification_date)
        print(f"Se han recogido {len(posts)} movimientos hasta {modification_date}")
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