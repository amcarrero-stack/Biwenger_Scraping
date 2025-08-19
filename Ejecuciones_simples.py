from collections import Counter
from bloque_bbdd import *
import locale
from datetime import datetime, date
from bloque_1_selenium import traducir_mes
from utils import print_usuarios
locale.setlocale(locale.LC_TIME, "C")

#crear tablas si no existen
# conn = get_db_connection()
# crear_tablas_si_no_existen(conn)
# cerrar_BBDD(conn)

# BORRAR USUARIOS
conn = get_db_connection()
borrar_todos_los_usuarios(conn)
print_usuarios(obtener_userinfo_bbdd(conn))

# BORRAR MOVIMIENTOS
borrar_todos_los_movimientos(conn)


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
# datos_to_update = [
#     {"id": 17, "modificationDate": "2025-08-16", "saldo": -3039410, "num_jugadores": 13},
#     {"id": 18, "modificationDate": "2025-08-16", "saldo": 2447900, "num_jugadores": 11},
#     {"id": 19, "modificationDate": "2025-08-16", "saldo": 53350, "num_jugadores": 11},
#     {"id": 20, "modificationDate": "2025-08-16", "saldo": 140150, "num_jugadores": 11},
#     {"id": 21, "modificationDate": "2025-08-16", "saldo": -2332740, "num_jugadores": 12},
#     {"id": 22, "modificationDate": "2025-08-16", "saldo": -1847210, "num_jugadores": 11},
#     {"id": 23, "modificationDate": "2025-08-16", "saldo": 187902, "num_jugadores": 12},
#     {"id": 24, "modificationDate": "2025-08-16", "saldo": -2883008, "num_jugadores": 13}
# ]
#
# actualizar_varios(
#     conn,
#     "usuarios",
#     datos_to_update,
#     condicion_campo="id"
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

# print(Path(__file__).parent)

# fecha_inicio_str = "2025-08-01 00:00:00"
# print(type(datetime.strptime(fecha_inicio_str, "%Y-%m-%d %H:%M:%S")))

# fecha_inicio_str = "2025-08-01 00:00:00.000"
# fecha = datetime.strptime(fecha_inicio_str, "%Y-%m-%d %H:%M:%S.%f")
# print(fecha)

# fecha_hoy = datetime.today()
# fecha_sin_micro = fecha_hoy.replace(microsecond=0)
# print(type(fecha_sin_micro))

