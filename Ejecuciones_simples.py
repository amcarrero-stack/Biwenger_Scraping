from collections import Counter
from bloque_bbdd import *
import locale
from datetime import datetime, date
from bloque_1_selenium import traducir_mes
from utils import print_usuarios

#crear tablas si no existen
# conn = get_db_connection()
# crear_tablas_si_no_existen(conn)
# cerrar_BBDD(conn)

# # BORRAR USUARIOS
# conn = get_db_connection()
# borrar_todos_los_usuarios(conn)
# print_usuarios(obtener_userinfo_bbdd(conn))
#
# # BORRAR MOVIMIENTOS
# conn = get_db_connection()
# borrar_todos_los_movimientos(conn)


# locale.setlocale(locale.LC_TIME, "C")  # Fuerza el formato inglés estándar
# #
# modification_date = '1 Aug 2025'
# cutoff_datetime = datetime.strptime(modification_date, "%d %b %Y")
# print(cutoff_datetime)

# locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
# fecha_hoy = datetime.today()
# print(fecha_hoy)
# print(type(fecha_hoy))
# fecha_formateada = fecha_hoy.strftime("%d %b %Y").replace('.', '')  # en Linux/Mac, para Windows usar diferente
#
# print(fecha_formateada)

# ACTUALIZAR DATOS DE LA TABLA
# conn = get_db_connection()
# actualizar_varios(
#     conn,
#     "usuarios",
#     [
#         {"id": "Juanjo", "modificationDate": "11 ago 2025"},
#         {"id": "David", "modificationDate": "11 ago 2025"},
#         {"id": "Jaime Palomino Cano", "modificationDate": "11 ago 2025"},
#         {"id": "Al-khelaifi", "modificationDate": "11 ago 2025"},
#         {"id": "Yyoquese", "modificationDate": "11 ago 2025"},
#         {"id": "Mast-antonio", "modificationDate": "11 ago 2025"},
#         {"id": "Bellingham5", "modificationDate": "11 ago 2025"},
#         {"id": "Bellingham5", "modificationDate": "11 ago 2025"}
#     ],
#     condicion_campo="name"
# )
# cerrar_BBDD(conn)

# INSERTA DATOS EN UNA TABLA
# movimientos_realizados = [
#     {"usuario_id": "8", "tipo":"fichaje", "jugador": "Tullido", "cantidad": 200000, "fecha":"13 ago 2025"},
#     {"usuario_id": "12", "tipo": "venta", "jugador": "Mbappe", "cantidad": -20000000, "fecha": "13 ago 2025"},
#     {"usuario_id": "13", "tipo":"clausulazo", "jugador": "Vinicius", "cantidad": 15000000, "fecha":"13 ago 2025"},
# ]
# insertar_varios("movimientos", movimientos_realizados)


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

print(Path(__file__).parent)