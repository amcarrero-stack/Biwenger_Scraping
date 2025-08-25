from collections import Counter
from bloque_bbdd import *
import locale
from datetime import datetime, date
from utils import *
from bloque_1_selenium import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
locale.setlocale(locale.LC_TIME, "C")

# # BORRAR USUARIOS
# conn = get_db_connection()
# borrar_todos_los_usuarios(conn)
# print_usuarios(obtener_userinfo_bbdd(conn))
#
# # BORRAR MOVIMIENTOS
# borrar_todos_los_movimientos(conn)

# ACTUALIZAR DATOS DE LA TABLA
conn = get_db_connection()
# datos_to_update = [
#     {"id": 97, "modificationDate": "2025-08-16", "saldo": -3039410, "num_jugadores": 13},
#     {"id": 98, "modificationDate": "2025-08-16", "saldo": 2447900, "num_jugadores": 11},
#     {"id": 99, "modificationDate": "2025-08-16", "saldo": 53350, "num_jugadores": 11},
#     {"id": 100, "modificationDate": "2025-08-16", "saldo": 140150, "num_jugadores": 11},
#     {"id": 101, "modificationDate": "2025-08-16", "saldo": -2332740, "num_jugadores": 12},
#     {"id": 102, "modificationDate": "2025-08-16", "saldo": -1847210, "num_jugadores": 11},
#     {"id": 103, "modificationDate": "2025-08-16", "saldo": 187902, "num_jugadores": 12},
#     {"id": 104, "modificationDate": "2025-08-16", "saldo": -2883008, "num_jugadores": 13}
# ]

datos_to_update = [
    {"id": 249, "modificationDate": "2025-08-20 00:00:00"},
    {"id": 250, "modificationDate": "2025-08-20 00:00:00"},
    {"id": 251, "modificationDate": "2025-08-20 00:00:00"},
    {"id": 252, "modificationDate": "2025-08-20 00:00:00"},
    {"id": 253, "modificationDate": "2025-08-20 00:00:00"},
    {"id": 254, "modificationDate": "2025-08-20 00:00:00"},
    {"id": 255, "modificationDate": "2025-08-20 00:00:00"},
    {"id": 256, "modificationDate": "2025-08-20 00:00:00"}
]

actualizar_varios(
    conn,
    "usuarios",
    datos_to_update,
    condicion_campo="id"
)
cerrar_BBDD(conn)

# INSERTA DATOS EN UNA TABLA
# conn = get_db_connection()
# movimientos_realizados = [
#     {"usuario_id": "8", "tipo":"fichaje", "jugador": "Tullido", "cantidad": 200000, "fecha":"13 ago 2025"},
#     {"usuario_id": "12", "tipo": "venta", "jugador": "Mbappe", "cantidad": -20000000, "fecha": "13 ago 2025"},
#     {"usuario_id": "13", "tipo":"clausulazo", "jugador": "Vinicius", "cantidad": 15000000, "fecha":"13 ago 2025"},
# ]
# insertar_varios(conn, "movimientos", movimientos_realizados)

# jugadores = [
#     {"nombre": "Badé", "posicion": "Defensa", "equipo": "Sevilla"}
# ]
# insertar_varios(conn, "jugadores", jugadores)
# cerrar_BBDD(conn)


# conn = get_db_connection()
# user_dict = obtener_userIds(conn)
# resumen_movimientos = obtener_resumen_movimientos(conn, user_dict)
# print(resumen_movimientos)
# saldos_actualizados = obtener_saldos_actualizados(conn, resumen_movimientos)
# print(saldos_actualizados)
# cerrar_BBDD(conn)

# conn = get_db_connection()
# user_dict = obtener_userIds(conn)
# resumen_movimientos_hoy = obtener_resumen_movimientos_hoy(conn, user_dict)
# print(resumen_movimientos_hoy)
# cerrar_BBDD(conn)


# fecha_inicio_str = "14 ago 2025"
# locale.setlocale(locale.LC_TIME, "C")
# fecha_str_traducida = traducir_mes(fecha_inicio_str)
# cutoff_datetime = datetime.strptime(fecha_str_traducida, "%d %b %Y")

# locale.setlocale(locale.LC_TIME, "C")
# fecha_str = "14 Aug 2025"
# fecha_dt = datetime.strptime(fecha_str, "%d %b %Y").date()  # Parseamos a datetime
#
# print(fecha_dt)
# print(type(fecha_dt))

# print("Antes:", locale.getlocale(locale.LC_TIME))

# print(Path(__file__).parent)

# fecha_inicio_str = "2025-08-01 00:00:00"
# print(type(datetime.strptime(fecha_inicio_str, "%Y-%m-%d %H:%M:%S")))

# fecha_inicio_str = "2025-08-01 00:00:00.000"
# fecha = datetime.strptime(fecha_inicio_str, "%Y-%m-%d %H:%M:%S.%f")
# print(fecha)

# fecha_hoy = datetime.today()
# fecha_sin_micro = fecha_hoy.replace(microsecond=0)
# print(type(fecha_sin_micro))


# options = Options()
# options.add_argument("--start-maximized")
# options.add_argument("--disable-save-password-bubble")
# options.add_experimental_option("prefs", {
#     "credentials_enable_service": False,
#     "profile.password_manager_enabled": False
# })
# driver = webdriver.Chrome(options=options)
# do_login(driver)
# time.sleep(3)
# driver.get(URL_BIWENGER_HOME)
# time.sleep(5)
# #Localizas el <select>
# select_element = driver.find_element(By.CSS_SELECTOR, "div.tools select.pl")

# #Creas el objeto Select
# select_obj = Select(select_element)

# #Opción 1: seleccionar por el texto visible
# select_obj.select_by_visible_text("Jornadas")
# time.sleep(2)
#
# try:
#     all_posts = driver.find_elements(By.CSS_SELECTOR, 'league-board-post')
#     last_post = all_posts[0]
#     children = last_post.find_elements(By.XPATH, "./*")
#     print(f"El contenedor tiene {len(children)} hijos")
#     for child in children:
#         print(child.tag_name, child.text)
    # numero_de_jornada = last_post.find_element(By.CSS_SELECTOR, "h3 a").text.strip()
    # time_relative = last_post.find_element(By.CSS_SELECTOR, "time-relative")
    # fecha_sin_formato = time_relative.get_attribute("title")
    # tr_list = last_post.find_elements(By.CSS_SELECTOR, 'div.content tr')
    # for row in tr_list:
    #     td_list = row.find_elements(By.CSS_SELECTOR, 'td')
    #     user_name = td_list[1].find_element(By.CSS_SELECTOR, "a").text
    #     valor = td_list[3].find_element(By.CSS_SELECTOR, "increment").text.replace(" €","").replace(".","")
    #     print(f"user_name es {user_name}")
    #     print(f"valor es {valor}")

# except Exception as e:
#     print("❌ El div.prueba no existe en el primer card")


# tu string original
# fecha_str = '20/8/25, 17:03'
#
# # lo conviertes en datetime
# fecha_dt = datetime.strptime(fecha_str, "%d/%m/%y, %H:%M")
#
# print("Datetime:", fecha_dt)

# conn = get_db_connection()
# delete_registros_table(conn, 'jugadores')
# cerrar_BBDD(conn)

# conn = get_db_connection()
# agregar_campos('jugadores', {"modificationDate": "DATE"}, conn)
# cerrar_BBDD(conn)


# # CARGA INICIAL DE TODOS LOS JUGADORES
# jugadores_actuales = obtener_registros_tabla(conn, 'jugadores', ['id', 'nombre'])
# if len(jugadores_actuales) != number_of_players(driver):
#     delete_registros_table(conn, 'jugadores')
#     jugadores_to_insert = set_all_players(driver)
#     insertar_varios(conn, 'jugadores', jugadores_to_insert)
#     jugadores_actuales = len(obtener_registros_tabla(conn, 'jugadores'))