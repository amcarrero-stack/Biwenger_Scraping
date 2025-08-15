import time
from datetime import datetime, timedelta

from config import URL_BIWENGER_HOME, NOMBRE_MI_EQUIPO, URL_BIWENGER_LIGA
from utils import log_message, crear_driver
from bloque_1_selenium import get_posts_until_date, obtenerMovimientos, obtener_ventas_y_compras, do_login, do_obtener_usuarios
from bloque_bbdd import *
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
        print(f"Usuarios detectados: {[u['name'] for u in usuarios_actuales]}")
        usuarios_db = obtener_userinfo_bbdd(conn)
        if not usuarios_db:
            insertar_usuarios(conn, usuarios_actuales)
            usuarios_db = obtener_userinfo_bbdd(conn)
        modification_date = usuarios_db[0][5]
        print(f'modification_date es {modification_date}')
        print(type(modification_date))
        print_usuarios(obtener_userinfo_bbdd(conn))
        posts = get_posts_until_date(driver, modification_date)
        print(f"Se han recogido {len(posts)} movimientos hasta {modification_date}")
        movimientos_to_insert = obtenerMovimientos(posts)
        print(f"movimientos_to_insert es {movimientos_to_insert}")
        insertar_varios('movimientos', movimientos_to_insert)

        # compras_y_ventas = obtener_ventas_y_compras(posts)
        # print(compras_y_ventas)

        user_dict = obtener_userId(conn)
        resumen_movimientos = obtener_resumen_movimientos(conn, user_dict, modification_date)
        print(resumen_movimientos)
        saldos_actualizados = obtener_saldos_actualizados(conn, resumen_movimientos)
        print(saldos_actualizados)
        actualizar_saldos_new(conn, saldos_actualizados)
        actualizar_num_jugadores(conn, usuarios_actuales)
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