from collections import Counter
from bloque_bbdd import get_db_connection, crear_tablas_si_no_existen, cerrar_BBDD, insertar_usuario, obtener_usuarios, print_usuarios, borrar_todos_los_usuarios
import locale
from datetime import datetime, date

# Borrar usuarios
conn = get_db_connection()
borrar_todos_los_usuarios(conn)
# print_usuarios(obtener_usuarios(conn))

locale.setlocale(locale.LC_TIME, "C")  # Fuerza el formato inglés estándar
#
modification_date = '1 Aug 2025'
cutoff_datetime = datetime.strptime(modification_date, "%d %b %Y")
print(cutoff_datetime)
