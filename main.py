from utils import log_message, crear_driver, print_usuarios, iniciar_log, log_message_with_print
from bloque_1_selenium import *
from bloque_bbdd import *
import traceback

def main():
    iniciar_log()
    log_message_with_print("🟢 === Inicio ejecución script Biwenger === 🟢")

    try:
        conn = get_db_connection()
        crear_tablas_si_no_existen(conn)
        # Crear driver
        driver = crear_driver()
        log_message_with_print("🌐 Navegando a la página principal de Biwenger...")
        do_login(driver)
        time.sleep(3)

        jugadores_actuales = obtener_registros_tabla(conn, 'jugadores', ['id', 'nombre'], '', '')
        if not jugadores_actuales:
            jugadores_to_insert = set_all_players(driver)
            insertar_varios(conn, 'jugadores', jugadores_to_insert)

        usuarios_actuales = do_obtener_usuarios(driver)
        log_message(f"Usuarios detectados: {[u['name'] for u in usuarios_actuales]}")
        usuarios_db = obtener_userinfo_bbdd(conn)
        if not usuarios_db:
            insertar_usuarios(conn, usuarios_actuales)
            usuarios_db = obtener_userinfo_bbdd(conn)
        modification_date = usuarios_db[0][5]
        user_dict = obtener_userIds(conn)
        user_names_dict = obtener_userNames(conn)
        print_usuarios(obtener_userinfo_bbdd(conn))

        posts = get_posts_until_date(driver, modification_date)
        log_message(f"Se han recogido {len(posts)} movimientos hasta {modification_date}")
        posts_wrapper = obtener_posts_wrapper(posts)
        movimientos_to_insert = procesar_posts(posts_wrapper, user_dict)
        log_message(f'moviemientos to insert es {movimientos_to_insert}')
        insertar_varios(conn, 'movimientos', movimientos_to_insert)

        jugadores_actuales = obtener_registros_tabla(conn, 'jugadores', ['id', 'nombre'])
        jugadores_actuales_dict = obtener_jugadores_dict(jugadores_actuales)
        movimientos_bbdd = obtener_registros_tabla(conn, 'movimientos', ['id', 'jugador','accion'], f"tipo='movimiento' AND fecha >= '{modification_date}' AND fecha <= datetime('now')", '')
        log_message(f'movimientos_bbdd es: {movimientos_bbdd}')
        movimientos_jugadores = obtener_movimientos_jugadores(movimientos_bbdd, jugadores_actuales_dict)
        procesar_movimientos_jugadores(movimientos_jugadores, conn)

        resumen_movimientos = obtener_resumen_movimientos(conn, user_dict, modification_date)
        log_message(resumen_movimientos)
        log_message(f"Resumen movimientos por usuario: {resumen_movimientos}")
        saldos_actualizados = obtener_saldos_actualizados(conn, resumen_movimientos)
        log_message(f"Saldos actualizados: {print_saldos_actualizados(conn, saldos_actualizados)}")
        actualizar_saldos_new(conn, saldos_actualizados)
        insertar_historial_usuarios(conn)
        resetear_propietarios_jugadores(conn)
        actualizar_propietarios_jugadores(conn, usuarios_actuales)

    except Exception as e:
        log_message_with_print(f"❌ Error durante la ejecución: {e}")
        traceback.print_exc()

    finally:
        if 'conn' in locals() and conn:
            cerrar_BBDD(conn)
        if 'driver' in locals():
            driver.quit()
        log_message_with_print("🟢 === Fin ejecución script Biwenger === 🟢")

if __name__ == "__main__":
    main()