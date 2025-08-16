from utils import log_message, crear_driver, print_usuarios, iniciar_log
from bloque_1_selenium import get_posts_until_date, obtenerMovimientos, do_login, do_obtener_usuarios
from bloque_bbdd import *
import traceback

def main():
    logFilePath = iniciar_log()
    log_message(logFilePath, "=== Inicio ejecución script Biwenger ===")

    try:
        conn = get_db_connection()
        crear_tablas_si_no_existen(conn)

        driver = crear_driver(logFilePath)
        log_message(logFilePath, "🌐 Navegando a la página principal de Biwenger...")
        do_login(driver)
        usuarios_actuales = do_obtener_usuarios(driver)
        log_message(logFilePath, f"Usuarios detectados: {[u['name'] for u in usuarios_actuales]}")
        usuarios_db = obtener_userinfo_bbdd(conn)
        if not usuarios_db:
            insertar_usuarios(conn, usuarios_actuales)
            usuarios_db = obtener_userinfo_bbdd(conn)
        modification_date = usuarios_db[0][5]
        user_dict = obtener_userId(conn)
        print_usuarios(obtener_userinfo_bbdd(conn))
        movimientos_hoy = obtener_movimientos_hoy(conn)
        if movimientos_hoy:
            resumen_movimientos = obtener_resumen_movimientos(conn, user_dict, modification_date)
            log_message(logFilePath, resumen_movimientos)
            saldos_actualizados = obtener_saldos_actualizados_hoy(conn, resumen_movimientos)
            log_message(logFilePath, saldos_actualizados)
            actualizar_saldos_new(conn, saldos_actualizados)
            delete_movimientos(conn, movimientos_hoy)

        posts = get_posts_until_date(driver, modification_date)
        log_message(logFilePath, f"Se han recogido {len(posts)} movimientos hasta {modification_date}")
        movimientos_to_insert = obtenerMovimientos(posts)
        log_message(logFilePath, f"movimientos_to_insert es {movimientos_to_insert}")
        insertar_varios(conn, 'movimientos', movimientos_to_insert)

        resumen_movimientos = obtener_resumen_movimientos(conn, user_dict, modification_date)
        log_message(logFilePath, resumen_movimientos)
        saldos_actualizados = obtener_saldos_actualizados(conn, resumen_movimientos)
        log_message(logFilePath, saldos_actualizados)
        actualizar_saldos_new(conn, saldos_actualizados)
        actualizar_num_jugadores(conn, usuarios_actuales)

    except Exception as e:
        log_message(logFilePath, f"❌ Error durante la ejecución: {e}")
        traceback.print_exc()

    finally:
        if 'conn' in locals() and conn:
            cerrar_BBDD(conn)
        if 'driver' in locals():
            driver.quit()
        log_message(logFilePath, "=== Fin ejecución script Biwenger ===")

if __name__ == "__main__":
    main()