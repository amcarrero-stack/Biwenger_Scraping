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

        jugadores_actuales = obtener_players_bbdd(conn, driver)
        usuarios_actuales = do_obtener_usuarios(driver)
        usuarios_db = obtener_usuarios_bbdd(conn, driver, usuarios_actuales)
        modification_date = datetime.strptime(usuarios_db[0]['modificationDate'], "%Y-%m-%d %H:%M:%S")
        user_dict = obtener_userIds(conn)
        user_names_dict = obtener_userNames(conn)

        posts = get_posts_until_date(driver, modification_date)
        posts_wrapper = obtener_posts_wrapper(posts)
        movimientos_to_insert = procesar_posts_wrapper(posts_wrapper, user_dict)
        insertar_varios(conn, 'movimientos', movimientos_to_insert)

        movimientos_de_jugadores = obtener_movimientos_de_jugadores(conn, jugadores_actuales, modification_date)
        procesar_movimientos_de_jugadores(movimientos_de_jugadores, conn)

        resumen_movimientos = obtener_resumen_movimientos(conn, user_dict, modification_date)
        saldos_actualizados = obtener_saldos_actualizados(conn, resumen_movimientos)
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

def obtener_players_bbdd(conn, driver):
    jugadores_actuales = obtener_registros_tabla(conn, 'jugadores', ['id', 'nombre'])
    if not jugadores_actuales:
        jugadores_to_insert = set_all_players(driver)
        insertar_varios(conn, 'jugadores', jugadores_to_insert)
        jugadores_actuales = obtener_registros_tabla(conn, 'jugadores', ['id', 'nombre'])
    return jugadores_actuales
def obtener_usuarios_bbdd(conn, driver, usuarios_actuales):
    log_message(f"Usuarios detectados: {[u['name'] for u in usuarios_actuales]}")
    usuarios_db = obtener_registros_tabla(conn, 'usuarios', ['id', 'name', 'saldo', 'url_name', 'num_jugadores', 'modificationDate'])
    if not usuarios_db:
        insertar_usuarios(conn, usuarios_actuales)
        usuarios_db = obtener_registros_tabla(conn, 'usuarios', ['id', 'name', 'saldo', 'url_name', 'num_jugadores', 'modificationDate'])
    return usuarios_db

if __name__ == "__main__":
    main()