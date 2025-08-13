from collections import Counter
from bloque_bbdd import get_db_connection, crear_tablas_si_no_existen, cerrar_BBDD, insertar_usuarios, obtener_userinfo_bbdd, print_usuarios, borrar_todos_los_usuarios, actualizar_varios,insertar_varios,borrar_todos_los_movimientos
import locale
from datetime import datetime, date

#crear tablas si no existen
# conn = get_db_connection()
# crear_tablas_si_no_existen(conn)


# BORRAR USUARIOS
conn = get_db_connection()
borrar_todos_los_usuarios(conn)
# print_usuarios(obtener_userinfo_bbdd(conn))

# BORRAR MOVIMIENTOS
conn = get_db_connection()
borrar_todos_los_movimientos(conn)


# locale.setlocale(locale.LC_TIME, "C")  # Fuerza el formato inglés estándar
# #
# modification_date = '1 Aug 2025'
# cutoff_datetime = datetime.strptime(modification_date, "%d %b %Y")
# print(cutoff_datetime)

# locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
# fecha_hoy = datetime.today()
# fecha_formateada = fecha_hoy.strftime("%d %b %Y").replace('.', '')  # en Linux/Mac, para Windows usar diferente
#
# print(fecha_formateada)

# ACTUALIZAR DATOS DE LA TABLA
# conn = get_db_connection()
# actualizar_varios(
#     conn,
#     "usuarios",
#     [
#         {"name": "Juanjo", "modificationDate": "11 ago 2025"},
#         {"name": "David", "modificationDate": "11 ago 2025"},
#         {"name": "Jaime Palomino Cano", "modificationDate": "11 ago 2025"},
#         {"name": "Al-khelaifi", "modificationDate": "11 ago 2025"},
#         {"name": "Yyoquese", "modificationDate": "11 ago 2025"},
#         {"name": "Mast-antonio", "modificationDate": "11 ago 2025"},
#         {"name": "Bellingham5", "modificationDate": "11 ago 2025"}
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
