import sqlite3
from pathlib import Path
from datetime import datetime
import locale
from utils import traducir_mes, log_message, log_message_with_print

locale.setlocale(locale.LC_TIME, "C")

RUTA_BASE = Path(__file__).parent
DB_PATH = RUTA_BASE / "BBDD" / "biwenger_bbdd.db"

def get_db_connection():
    if not DB_PATH.parent.exists():
        DB_PATH.parent.mkdir(parents=True)
    conn = sqlite3.connect(DB_PATH)
    return conn

def crear_tablas_si_no_existen(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            url_name TEXT UNIQUE NOT NULL,
            saldo INTEGER NOT NULL,
            saldo_anterior INTEGER NOT NULL,
            num_jugadores INTEGER,
            modificationDate DATE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios_historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            saldo INTEGER NOT NULL,
            num_jugadores INTEGER,
            modificationDate DATE,
            tipo_actualizacion TEXT CHECK(tipo_actualizacion IN ('delete', 'update', 'insert')),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            tipo TEXT CHECK(tipo IN ('fichaje', 'venta', 'clausulazo', 'abono', 'penalizacion')),
            jugador TEXT,
            cantidad REAL,
            fecha DATE,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    ''')
    conn.commit()

# Insertar un usuario
def insertar_usuarios(conn, usuarios):
    locale.setlocale(locale.LC_TIME, "C")
    cursor = conn.cursor()
    for user in usuarios:
        name = user['name']
        url_name = user['url_name']
        num_jugadores = user['num_jug']

        fecha_inicio_str = "2025-08-01 00:00:00"
        fecha_inicio_sql = datetime.strptime(fecha_inicio_str, "%Y-%m-%d %H:%M:%S")

        saldo = 40000000

        cursor.execute('''
            INSERT INTO usuarios (name, url_name, saldo, saldo_anterior, num_jugadores, modificationDate)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, url_name, saldo, saldo, num_jugadores, fecha_inicio_sql))
    conn.commit()

def borrar_todos_los_usuarios(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios")
        conn.commit()
        print("Todos los usuarios han sido eliminados.")
    except Exception as e:
        print(f"Error al borrar los usuarios {e}")


def borrar_todos_los_movimientos(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM movimientos")
        conn.commit()
        print("Todos los movimientos han sido eliminados.")
    except Exception as e:
        print(f"Error al borrar los movimientos {e}")

def obtener_userinfo_bbdd(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, saldo, url_name, num_jugadores, modificationDate
        FROM usuarios
    """)
    usuarios = cursor.fetchall()

    # Convertir la fecha a datetime.date si viene como string
    usuarios_convertidos = []
    for u in usuarios:
        fecha = u[5]
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")
        usuarios_convertidos.append((
            u[0], u[1], u[2], u[3], u[4], fecha
        ))

    return usuarios_convertidos



def obtener_userIds(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM usuarios")
    usuarios = cursor.fetchall()

    # Crear diccionario: key = name, value = id
    user_dict = {name: uid for uid, name in usuarios}
    return user_dict

def obtener_userNames(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM usuarios")
    usuarios = cursor.fetchall()

    # Crear diccionario: key = name, value = id
    user_names_dict = {uid: name for uid, name in usuarios}
    return user_names_dict

def obtener_saldos(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, saldo FROM usuarios")
    usuarios = cursor.fetchall()

    # Crear diccionario: key = name, value = id
    user_dict = {uid: saldo for uid, saldo in usuarios}
    return user_dict

def obtener_movimientos_hoy(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movimientos WHERE fecha = date('now')")

    return cursor.fetchall()

def delete_movimientos(conn, movimientos):
    cursor = conn.cursor()
    for mov in movimientos:
        # Aquí asumo que el id del movimiento está en la primera posición de la tupla
        cursor.execute("DELETE FROM movimientos WHERE id = ?", (mov[0],))
    conn.commit()

def cerrar_BBDD(conn):
    conn.close()

def actualizar_saldos_new(conn, nuevos_saldos):
    log_message_with_print("🌐 Actualizando los saldos...")
    cursor = conn.cursor()
    # Obtener la fecha actual en formato "5 ago 2025"
    fecha_hoy = datetime.today().replace(microsecond=0)
    saldos_actuales_by_userId = obtener_saldos(conn)

    # Normaliza a lista de tuplas (saldo, modificationDate, id)
    if isinstance(nuevos_saldos, dict):
        pares = [(int(saldo), fecha_hoy, int(saldos_actuales_by_userId[uid]), int(uid)) for uid, saldo in nuevos_saldos.items()]
    else:
        # asumimos iterable de dicts con keys 'usuario_id' y 'saldo'
        pares = [(int(item['saldo']), fecha_hoy, int(saldos_actuales_by_userId[item['usuario_id']]), int(item['usuario_id'])) for item in nuevos_saldos]

    log_message('Pares en actualizar_saldos_new es:')
    log_message(pares)
    # Actualizamos saldo y modificationDate
    cursor.executemany(
        "UPDATE usuarios SET saldo = ?, modificationDate = ?, saldo_anterior = ?  WHERE id = ?",
        pares
    )
    conn.commit()

def actualizar_num_jugadores(conn, array_usuarios):
    log_message_with_print("🌐 Actualizando el numero de jugadores...")
    """
    Actualiza la columna num_jugadores en la tabla usuarios a partir del array de usuarios
    y del diccionario que devuelve obtener_userId.
    """
    cursor = conn.cursor()

    # Obtenemos el diccionario {name: usuario_id}
    user_ids = obtener_userIds(conn)

    for usuario in array_usuarios:
        name = usuario['name']
        num_jug = usuario['num_jug']

        # Saltar usuarios que no estén en la BBDD (por ejemplo Pierre Nodoyuna)
        if name not in user_ids:
            continue

        usuario_id = user_ids[name]

        # Actualizamos num_jugadores
        cursor.execute(
            "UPDATE usuarios SET num_jugadores = ? WHERE id = ?",
            (num_jug, usuario_id)
        )
    conn.commit()

def actualizar_registro(conn, tabla, valores, condicion_campo, condicion_valor):
    """
    Actualiza un registro en la base de datos de forma dinámica.

    conn: conexión sqlite3
    tabla: str → nombre de la tabla
    valores: dict → {'campo1': valor1, 'campo2': valor2, ...}
    condicion_campo: str → campo para la condición WHERE
    condicion_valor: valor de la condición
    """
    # Genera dinámicamente "campo1 = ?, campo2 = ?"
    set_clause = ", ".join([f"{campo} = ?" for campo in valores.keys()])

    # Construye la query
    query = f"UPDATE {tabla} SET {set_clause} WHERE {condicion_campo} = ?"

    # Ejecuta con los valores más la condición
    params = list(valores.values()) + [condicion_valor]

    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()

def actualizar_varios(conn, tabla, lista_valores, condicion_campo):
    for item in lista_valores:
        condicion_valor = item.pop(condicion_campo)
        actualizar_registro(conn, tabla, item, condicion_campo, condicion_valor)


def insertar_registro(conn, tabla, valores):
    """
    Inserta un registro en la tabla de forma dinámica.

    conn: conexión sqlite3
    tabla: str → nombre de la tabla
    valores: dict → {'campo1': valor1, 'campo2': valor2, ...}
    """
    campos = ", ".join(valores.keys())
    placeholders = ", ".join(["?"] * len(valores))
    query = f"INSERT INTO {tabla} ({campos}) VALUES ({placeholders})"

    cursor = conn.cursor()
    cursor.execute(query, list(valores.values()))
    conn.commit()

def insertar_varios(conn, tabla, lista_valores):
    log_message_with_print("🌐 Insertando movimientos post...")
    """
    Inserta varios registros en la tabla a partir de una lista de diccionarios.
    """
    for item in lista_valores:
        insertar_registro(conn, tabla, item)

def obtener_resumen_movimientos(conn, user_dict, fecha_inicio_str):
    log_message_with_print("🌐 Obteniendo resumen de los movimientos insertados...")
    cursor = conn.cursor()
    resultados = []
    fecha_hoy = datetime.today()
    for nombre, user_id in user_dict.items():
        resumen = {'usuario_id': user_id}

        # Ventas
        cursor.execute("""
            SELECT COALESCE(SUM(cantidad), 0)
            FROM movimientos
            WHERE usuario_id = ?
              AND tipo = 'venta'
              AND fecha BETWEEN ? AND ?
        """, (user_id, fecha_inicio_str, fecha_hoy))
        resumen['ventas'] = cursor.fetchone()[0]

        # Fichajes
        cursor.execute("""
            SELECT COALESCE(SUM(cantidad), 0)
            FROM movimientos
            WHERE usuario_id = ?
              AND tipo = 'fichaje'
              AND fecha BETWEEN ? AND ?
        """, (user_id, fecha_inicio_str, fecha_hoy))
        resumen['fichajes'] = cursor.fetchone()[0]

        # Penalizaciones
        cursor.execute("""
            SELECT COALESCE(SUM(cantidad), 0)
            FROM movimientos
            WHERE usuario_id = ?
              AND tipo = 'penalizacion'
              AND fecha BETWEEN ? AND ?
        """, (user_id, fecha_inicio_str, fecha_hoy))
        resumen['penalizaciones'] = cursor.fetchone()[0]

        # Clausulazos
        cursor.execute("""
            SELECT COALESCE(SUM(cantidad), 0)
            FROM movimientos
            WHERE usuario_id = ?
              AND tipo = 'clausulazo'
              AND fecha BETWEEN ? AND ?
        """, (user_id, fecha_inicio_str, fecha_hoy))
        resumen['clausulazos'] = cursor.fetchone()[0]

        resultados.append(resumen)

    return resultados
def obtener_saldos_actualizados(conn, movimientos):
    log_message_with_print("🌐 Obteniendo los saldos actualizados...")
    # Obtener saldos actuales de la BBDD
    saldos_actuales = obtener_saldos(conn)  # {usuario_id: saldo}

    # Recorrer cada movimiento y actualizar el saldo
    for mov in movimientos:
        usuario_id = mov['usuario_id']

        if usuario_id not in saldos_actuales:
            log_message(f"⚠ Usuario {usuario_id} no encontrado en BBDD, se omite.")
            continue

        saldo_inicial = saldos_actuales[usuario_id]

        # Aplicar sumas y restas
        saldo_final = (
                saldo_inicial
                + mov.get('ventas', 0)
                + mov.get('clausulazos', 0)
                + mov.get('fichajes', 0)  # ya viene negativo
                + mov.get('penalizaciones', 0)  # ya viene negativo
        )

        # Guardar el saldo final en el diccionario
        saldos_actuales[usuario_id] = saldo_final

    return saldos_actuales

def print_saldos_actualizados(conn, dict_id_saldos):
    dict_id_userName = obtener_userNames(conn)
    dict_username_saldos = {}

    for uid, saldo in dict_id_saldos.items():
        username = dict_id_userName.get(uid, f"ID_{uid}")  # si no existe el id, pone ID_xxx
        dict_username_saldos[username] = saldo

    return dict_username_saldos


def obtener_saldos_actualizados_hoy(conn, movimientos):
    # Obtener saldos actuales de la BBDD
    saldos_actuales = obtener_saldos(conn)  # {usuario_id: saldo}

    # Recorrer cada movimiento y actualizar el saldo
    for mov in movimientos:
        usuario_id = mov['usuario_id']

        if usuario_id not in saldos_actuales:
            log_message(f"⚠ Usuario {usuario_id} no encontrado en BBDD, se omite.")
            continue

        saldo_inicial = saldos_actuales[usuario_id]

        # Aplicar sumas y restas
        saldo_final = (
                saldo_inicial
                - mov.get('ventas', 0)
                - mov.get('clausulazos', 0)
                - mov.get('fichajes', 0)  # ya viene negativo
                - mov.get('penalizaciones', 0)  # ya viene negativo
        )

        # Guardar el saldo final en el diccionario
        saldos_actuales[usuario_id] = saldo_final

    return saldos_actuales