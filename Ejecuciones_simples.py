from collections import Counter
from bloque_bbdd import get_db_connection, crear_tablas_si_no_existen, cerrar_BBDD, insertar_usuario, obtener_usuarios, print_usuarios, borrar_todos_los_usuarios

# Borrar usuarios
conn = get_db_connection()
# borrar_todos_los_usuarios(conn)
print_usuarios(obtener_usuarios(conn))
