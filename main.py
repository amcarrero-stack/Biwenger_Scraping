from utils import log_message, crear_driver, print_usuarios, iniciar_log, log_message_with_print
from bloque_1_selenium import do_login, obtener_usuarios_web, get_posts_until_date, obtener_posts_wrapper, procesar_posts_wrapper, set_all_players, obtener_movimientos_de_jugadores
from bloque_bbdd import *
import traceback
import time
from datetime import datetime

# ============================
# Context Managers Helpers
# ============================

from contextlib import contextmanager

# ============================
# Main Logic
# ============================

def main():
    iniciar_log()
    log_message_with_print("🟢 === Inicio ejecución script Biwenger === 🟢")

    try:
        with db_connection() as conn, selenium_driver() as driver:

            jugadores_actuales = obtener_players_bbdd(conn, driver)
            usuarios_actuales = obtener_usuarios_web(driver)
            usuarios_db = obtener_usuarios_bbdd(conn, usuarios_actuales)
            print(f'usuarios_db es : {usuarios_db}')
            modification_date = get_latest_modification_date(usuarios_db)
            time.sleep(2)
            user_dict = obtener_userIds(conn)
            print(f'user_dict es : {user_dict}')
            # Procesar posts
            posts = get_posts_until_date(driver, modification_date)
            posts_wrapper = obtener_posts_wrapper(posts)
            movimientos_to_insert = procesar_posts_wrapper(posts_wrapper, user_dict)
            insertar_varios(conn, 'movimientos', movimientos_to_insert)

            # Movimientos de jugadores
            movimientos_de_jugadores = obtener_movimientos_de_jugadores(conn, jugadores_actuales, modification_date)
            procesar_movimientos_de_jugadores(movimientos_de_jugadores, conn)

            # Resumen y actualización de saldos
            resumen_movimientos = obtener_resumen_movimientos(conn, user_dict, modification_date)
            saldos_actualizados = obtener_saldos_actualizados(conn, resumen_movimientos)
            actualizar_saldos_new(conn, saldos_actualizados)

            # Historial y actualización de jugadores
            insertar_historial_usuarios(conn)
            resetear_propietarios_jugadores(conn)
            actualizar_propietarios_jugadores(conn, usuarios_actuales)

    except Exception as e:
        log_message_with_print(f"❌ Error durante la ejecución: {e}")
        traceback.print_exc()
    finally:
        log_message_with_print("🟢 === Fin ejecución script Biwenger === 🟢")

@contextmanager
def db_connection():
    conn = get_db_connection()
    try:
        crear_tablas_si_no_existen(conn)
        yield conn
    finally:
        cerrar_BBDD(conn)

@contextmanager
def selenium_driver():
    driver = crear_driver()
    try:
        do_login(driver)
        time.sleep(3)  # Mejor usar WebDriverWait si es posible
        yield driver
    finally:
        driver.quit()

# ============================
# Funciones de utilidad
# ============================

def obtener_o_crear_registros(conn, tabla, registros, campos, insertar_func):
    existentes = obtener_registros_tabla(conn, tabla, campos)
    if not existentes:
        insertar_func(conn, registros)
        existentes = obtener_registros_tabla(conn, tabla, campos)
    return existentes

def obtener_players_bbdd(conn, driver):
    jugadores_actuales = obtener_registros_tabla(conn, 'jugadores', ['id', 'nombre'])
    if not jugadores_actuales:
        jugadores_to_insert = set_all_players(driver)
        insertar_varios(conn, 'jugadores', jugadores_to_insert)
        jugadores_actuales = obtener_registros_tabla(conn, 'jugadores', ['id', 'nombre'])
    return jugadores_actuales

def obtener_usuarios_bbdd(conn, usuarios_actuales):
    log_message(f"Usuarios detectados: {[u['name'] for u in usuarios_actuales]}")
    return obtener_o_crear_registros(
        conn,
        'usuarios',
        usuarios_actuales,
        ['id', 'name', 'saldo', 'url_name', 'num_jugadores', 'modificationDate'],
        insertar_usuarios
    )

def get_latest_modification_date(usuarios_db):
    if not usuarios_db:
        raise ValueError("No hay usuarios en la base de datos")

    # Postgres devuelve las columnas en minúscula
    mod_date = usuarios_db[0].get('modificationdate')

    if isinstance(mod_date, str):
        return datetime.strptime(mod_date, "%Y-%m-%d %H:%M:%S")
    return mod_date

# ============================
# Entry Point
# ============================

if __name__ == "__main__":
    main()
