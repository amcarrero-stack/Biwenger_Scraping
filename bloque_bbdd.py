import sqlite3
from pathlib import Path
from datetime import datetime
import locale

# Asegúrate de establecer el locale en español para los nombres de los meses
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')  # En Windows puede ser 'Spanish_Spain'

RUTA_BASE = Path(__file__).parent
DB_PATH = RUTA_BASE / "BBDD" / "biwenger.db"

def get_db_connection():
    if not DB_PATH.parent.exists():
        DB_PATH.parent.mkdir(parents=True)
    conn = sqlite3.connect(DB_PATH)
    return conn

def crear_tablas_si_no_existen(conn):
    cursor = conn.cursor()
    # cursor.execute('''
    #     CREATE TABLE IF NOT EXISTS usuarios (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         name TEXT UNIQUE NOT NULL,
    #         url_name TEXT UNIQUE NOT NULL,
    #         saldo INTEGER NOT NULL,
    #         num_jugadores INTEGER,
    #         modificationDate TEXT
    #     )
    # ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            tipo TEXT CHECK(tipo IN ('fichaje', 'venta', 'clausulazo', 'abono', 'penalizacion')),
            jugador TEXT,
            cantidad REAL,
            fecha TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    ''')
    conn.commit()

# Insertar un usuario
def insertar_usuarios(conn, usuarios):
    cursor = conn.cursor()
    for user in usuarios:
        name = user['name']
        url_name = user['url_name']
        num_jugadores = user['num_jug']
        modificationDate = '1 ago 2025' #fecha inicial del juego
        saldo = 40000000

        cursor.execute('''
            INSERT INTO usuarios (name, url_name, saldo, num_jugadores, modificationDate)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, url_name, saldo, num_jugadores, modificationDate))
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

# Consultar usuarios
def obtener_userinfo_bbdd(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, saldo, url_name, num_jugadores, modificationDate FROM usuarios")
    usuarios = cursor.fetchall()
    return usuarios


def obtener_userId(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM usuarios")
    usuarios = cursor.fetchall()

    # Crear diccionario: key = name, value = id
    user_dict = {name: uid for uid, name in usuarios}
    return user_dict

def obtener_saldos(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, saldo FROM usuarios")
    usuarios = cursor.fetchall()

    # Crear diccionario: key = name, value = id
    user_dict = {uid: saldo for uid, saldo in usuarios}
    return user_dict

def print_usuarios(usuarios):
    for usuario in usuarios:
        print(f"ID: {usuario[0]}, Nombre: {usuario[1]}, Saldo: {usuario[2]}, URL Name: {usuario[3]}, Jugadores: {usuario[4]}, Fecha: {usuario[5]}")

def cerrar_BBDD(conn):
    conn.close()

def actualizar_saldos(conn, movimientos):
    """
    Actualiza el saldo y modificationDate de cada usuario según los movimientos.

    :param conn: conexión a la base de datos SQLite.
    :param movimientos: lista de diccionarios con username, compras y ventas.
    """
    cursor = conn.cursor()

    # Obtener la fecha actual en formato "5 ago 2025"
    locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
    fecha_hoy = datetime.today()
    fecha_formateada = fecha_hoy.strftime("%d %b %Y").replace('.', '')

    for mov in movimientos:
        username = mov['username']
        compras = mov.get('compras', 0)
        ventas = mov.get('ventas', 0)
        penalizaciones = mov.get('penalizaciones', 0)

        # Obtener el saldo actual
        cursor.execute("SELECT saldo FROM usuarios WHERE name = ?", (username,))
        resultado = cursor.fetchone()

        if resultado:
            saldo_actual = resultado[0]
            saldo_nuevo = saldo_actual - compras + ventas - penalizaciones

            # Actualizar saldo y fecha
            cursor.execute(
                "UPDATE usuarios SET saldo = ?, modificationDate = ? WHERE name = ?",
                (saldo_nuevo, fecha_formateada, username)
            )
        else:
            print(f"⚠️ Usuario '{username}' no encontrado en la tabla usuarios.")

    conn.commit()
    print("✅ Saldos y fechas actualizados correctamente.")

def actualizar_saldos_new(conn, nuevos_saldos):
    cursor = conn.cursor()
    # Obtener la fecha actual en formato "5 ago 2025"
    locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
    fecha_hoy = datetime.today()
    fecha_formateada = fecha_hoy.strftime("%d %b %Y").replace('.', '')

    # Normaliza a lista de tuplas (saldo, modificationDate, id)
    if isinstance(nuevos_saldos, dict):
        pares = [(int(saldo), fecha_formateada, int(uid)) for uid, saldo in nuevos_saldos.items()]
    else:
        # asumimos iterable de dicts con keys 'usuario_id' y 'saldo'
        pares = [(int(item['saldo']), fecha_formateada, int(item['usuario_id'])) for item in nuevos_saldos]

    # Actualizamos saldo y modificationDate
    cursor.executemany(
        "UPDATE usuarios SET saldo = ?, modificationDate = ? WHERE id = ?",
        pares
    )
    conn.commit()

def actualizar_num_jugadores(conn, array_usuarios):
    """
    Actualiza la columna num_jugadores en la tabla usuarios a partir del array de usuarios
    y del diccionario que devuelve obtener_userId.
    """
    cursor = conn.cursor()

    # Obtenemos el diccionario {name: usuario_id}
    user_ids = obtener_userId(conn)

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

def insertar_varios(tabla, lista_valores):
    """
    Inserta varios registros en la tabla a partir de una lista de diccionarios.
    """
    conn = get_db_connection()
    for item in lista_valores:
        insertar_registro(conn, tabla, item)
    cerrar_BBDD(conn)

def obtener_resumen_movimientos(conn, user_dict):
    cursor = conn.cursor()
    resultados = []

    for nombre, user_id in user_dict.items():
        resumen = {'usuario_id': user_id}

        # Ventas
        cursor.execute("""
            SELECT COALESCE(SUM(cantidad), 0)
            FROM movimientos
            WHERE usuario_id = ? AND tipo = 'venta'
        """, (user_id,))
        resumen['ventas'] = cursor.fetchone()[0]

        # Fichajes
        cursor.execute("""
            SELECT COALESCE(SUM(cantidad), 0)
            FROM movimientos
            WHERE usuario_id = ? AND tipo = 'fichaje'
        """, (user_id,))
        resumen['fichajes'] = cursor.fetchone()[0]

        # Penalizaciones
        cursor.execute("""
            SELECT COALESCE(SUM(cantidad), 0)
            FROM movimientos
            WHERE usuario_id = ? AND tipo = 'penalizacion'
        """, (user_id,))
        resumen['penalizaciones'] = cursor.fetchone()[0]

        # Clausulazos
        cursor.execute("""
            SELECT COALESCE(SUM(cantidad), 0)
            FROM movimientos
            WHERE usuario_id = ? AND tipo = 'clausulazo'
        """, (user_id,))
        resumen['clausulazos'] = cursor.fetchone()[0]

        resultados.append(resumen)

    return resultados

def obtener_resumen_movimientos_hoy(conn, user_dict):
    cursor = conn.cursor()
    resultados = []
    locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
    fecha_hoy = datetime.today()
    fecha_formateada = fecha_hoy.strftime("%d %b %Y").replace('.', '')

    for nombre, user_id in user_dict.items():
        resumen = {'usuario_id': user_id}

        # Ventas
        cursor.execute("""
            SELECT COALESCE(SUM(cantidad), 0)
            FROM movimientos
            WHERE usuario_id = ? AND tipo = 'venta' AND fecha = ?
        """, (user_id, fecha_formateada))
        resumen['ventas'] = cursor.fetchone()[0]

        # Fichajes
        cursor.execute("""
            SELECT COALESCE(SUM(cantidad), 0)
            FROM movimientos
            WHERE usuario_id = ? AND tipo = 'fichaje' AND fecha = ?
        """, (user_id, fecha_formateada))
        resumen['fichajes'] = cursor.fetchone()[0]

        # Penalizaciones
        cursor.execute("""
            SELECT COALESCE(SUM(cantidad), 0)
            FROM movimientos
            WHERE usuario_id = ? AND tipo = 'penalizacion' AND fecha = ?
        """, (user_id, fecha_formateada))
        resumen['penalizaciones'] = cursor.fetchone()[0]

        # Clausulazos
        cursor.execute("""
            SELECT COALESCE(SUM(cantidad), 0)
            FROM movimientos
            WHERE usuario_id = ? AND tipo = 'clausulazo' AND fecha = ?
        """, (user_id, fecha_formateada))
        resumen['clausulazos'] = cursor.fetchone()[0]

        resultados.append(resumen)

    return resultados


def obtener_saldos_actualizados(conn, movimientos):
    # Obtener saldos actuales de la BBDD
    saldos_actuales = obtener_saldos(conn)  # {usuario_id: saldo}

    # Recorrer cada movimiento y actualizar el saldo
    for mov in movimientos:
        usuario_id = mov['usuario_id']

        if usuario_id not in saldos_actuales:
            print(f"⚠ Usuario {usuario_id} no encontrado en BBDD, se omite.")
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