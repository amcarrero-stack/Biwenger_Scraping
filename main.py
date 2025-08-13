import time
from datetime import datetime, timedelta

from config import URL_BIWENGER_HOME, NOMBRE_MI_EQUIPO, URL_BIWENGER_LIGA
from utils import log_message, crear_driver
from bloque_1_selenium import get_posts_until_date, mostrar_texto_h3, obtener_ventas_y_compras
from bloque_1_selenium import do_login, do_obtener_usuarios
from bloque_bbdd import get_db_connection, crear_tablas_si_no_existen, cerrar_BBDD, insertar_usuarios, obtener_userinfo_bbdd, print_usuarios, actualizar_saldos, insertar_varios
import traceback

def main():
    log_message("=== Inicio ejecución script Biwenger ===")

    try:
        conn = get_db_connection()
        crear_tablas_si_no_existen(conn)

        driver = crear_driver()
        log_message("🌐 Navegando a la página principal de Biwenger...")
        do_login(driver)
        # input("🔒 Inicia sesión (si no lo estás) y pulsa Enter para continuar...")
        usuarios_actuales = do_obtener_usuarios(driver)
        print(f"Usuarios detectados (excluyendo {NOMBRE_MI_EQUIPO}): {[u['name'] for u in usuarios_actuales]}")
        usuarios_db = obtener_userinfo_bbdd(conn)
        if not usuarios_db:
            insertar_usuarios(conn, usuarios_actuales)
            usuarios_db = obtener_userinfo_bbdd(conn)
        modification_date = str(usuarios_db[0][5]).strip()
        print(f'modification_date es {modification_date}')
        print_usuarios(obtener_userinfo_bbdd(conn))
        posts = get_posts_until_date(driver, modification_date)
        print(f"Se han recogido {len(posts)} movimientos hasta {modification_date}")
        movimientos_to_insert = mostrar_texto_h3(posts)
        print(f"movimientos_to_insert es {movimientos_to_insert}")
        insertar_varios('movimientos', movimientos_to_insert)
        compras_y_ventas = obtener_ventas_y_compras(posts)
        print(compras_y_ventas)
        actualizar_saldos(conn, compras_y_ventas)
        cerrar_BBDD(conn)

    except Exception as e:
        log_message(f"❌ Error durante la ejecución: {e}")
        traceback.print_exc()

    finally:
        if 'driver' in locals():
            driver.quit()
        log_message("=== Fin ejecución script Biwenger ===")

if __name__ == "__main__":
    main()