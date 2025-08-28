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

def cerrar_BBDD(conn):
    conn.close()
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
            usuario_id INTEGER,
            tipo TEXT CHECK(tipo IN ('fichaje', 'venta', 'clausulazo', 'abono', 'penalizacion', 'movimiento', 'cambioNombre')),
            jugador TEXT,
            cantidad REAL,
            fecha DATE,
            accion TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jugadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            nombre TEXT UNIQUE NOT NULL,
            valor REAL,
            posicion TEXT,
            equipo TEXT,
            href TEXT,
            modificationDate DATE,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuario_jugador_historial (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT,
            jugador_id INT,
            fecha DATE,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY (jugador_id) REFERENCES jugadores(id)
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

def obtener_registros_tabla(conn, tabla, campos=None, where=None, orderby=None):
    cursor = conn.cursor()

    # Selección de columnas
    if campos and len(campos) > 0:
        columnas = ", ".join(campos)
    else:
        columnas = "*"

    # Construcción de la query
    query = f"SELECT {columnas} FROM {tabla}"
    if where and where.strip() != "":
        query += f" WHERE {where}"
    if orderby and orderby.strip() != "":
        query += f" ORDER BY {orderby}"

    cursor.execute(query)
    registros = cursor.fetchall()

    # Obtener nombres de columnas seleccionadas
    col_names = [desc[0] for desc in cursor.description]

    # Convertir a lista de diccionarios
    resultado = [dict(zip(col_names, row)) for row in registros]

    return resultado

def obtener_jugadores_dict(jugadores):
    # Crear diccionario: key = name, value = id
    user_dict = {nombre: id for id, nombre in jugadores}
    return user_dict

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

def actualizar_propietarios_jugadores(conn, array_usuarios):
    log_message_with_print("🌐 Actualizando el numero de jugadores y propietarios de jugadores...")

    cursor = conn.cursor()

    # Obtenemos diccionarios necesarios
    user_ids = obtener_userIds(conn)  # {name: usuario_id}

    # Obtener lista de todos los jugadores desde BBDD (id, nombre)
    cursor.execute("SELECT id, nombre FROM jugadores")
    jugadores_bbdd = cursor.fetchall()
    jugador_dict = obtener_jugadores_dict(jugadores_bbdd)  # {nombre: id}

    for usuario in array_usuarios:
        name = usuario['name']
        num_jug = usuario['num_jug']
        plantilla = usuario.get('plantilla', [])

        # Saltar usuarios que no estén en la BBDD
        if name not in user_ids:
            continue

        usuario_id = user_ids[name]

        # Actualizamos num_jugadores en usuarios
        cursor.execute(
            "UPDATE usuarios SET num_jugadores = ? WHERE id = ?",
            (num_jug, usuario_id)
        )

        # Actualizamos el propietario de los jugadores
        for jugador_nombre in plantilla:
            if jugador_nombre in jugador_dict:
                jugador_id = jugador_dict[jugador_nombre]
                cursor.execute(
                    "UPDATE jugadores SET usuario_id = ? WHERE id = ?",
                    (usuario_id, jugador_id)
                )
            else:
                # Si el jugador no está en BBDD, opcionalmente logueamos
                log_message_with_print(f"⚠️ Jugador '{jugador_nombre}' no encontrado en la BBDD")

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
    """
    campos = ", ".join(valores.keys())
    placeholders = ", ".join(["?"] * len(valores))
    query = f"INSERT INTO {tabla} ({campos}) VALUES ({placeholders})"

    try:
        cursor = conn.cursor()
        cursor.execute(query, list(valores.values()))
        conn.commit()
        return True  # éxito
    except sqlite3.IntegrityError as e:
        print(f"❌ Error de integridad: {e} → {valores}")
        return False
    except sqlite3.Error as e:
        print(f"⚠️ Error SQLite: {e} → {valores}")
        return False

def insertar_varios(conn, tabla, lista_valores):
    # log_message_with_print("🌐 Insertando movimientos post...")
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

        # Clausulazos
        cursor.execute("""
            SELECT COALESCE(SUM(cantidad), 0)
            FROM movimientos
            WHERE usuario_id = ?
              AND tipo = 'abono'
              AND fecha BETWEEN ? AND ?
        """, (user_id, fecha_inicio_str, fecha_hoy))
        resumen['abonos'] = cursor.fetchone()[0]

        resultados.append(resumen)
    log_message(f"Resumen movimientos por usuario: {resultados}")
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
                + mov.get('abonos', 0)
        )

        # Guardar el saldo final en el diccionario
        saldos_actuales[usuario_id] = saldo_final

    log_message(f"Saldos actualizados: {print_saldos_actualizados(conn, saldos_actuales)}")
    return saldos_actuales

def print_saldos_actualizados(conn, dict_id_saldos):
    dict_id_userName = obtener_userNames(conn)
    dict_username_saldos = {}

    for uid, saldo in dict_id_saldos.items():
        username = dict_id_userName.get(uid, f"ID_{uid}")  # si no existe el id, pone ID_xxx
        dict_username_saldos[username] = saldo

    return dict_username_saldos

def resetear_propietarios_jugadores(conn):
    """
    Establece usuario_id a NULL para todos los jugadores en la tabla jugadores.
    """
    log_message_with_print("🌐 Reseteando propietarios de todos los jugadores...")

    cursor = conn.cursor()
    cursor.execute("UPDATE jugadores SET usuario_id = NULL")
    conn.commit()

def procesar_movimientos_de_jugadores(movimientos_jugadores, conn):
    """
    Procesa los movimientos de jugadores: elimina e inserta en la BBDD.
    movimientos_jugadores: lista con diccionarios { "recordsToDelete": [...], "recordsToInsert": [...] }
    conn: conexión SQLite
    """
    cursor = conn.cursor()

    for movimiento in movimientos_jugadores:
        # 🔴 Borrar registros
        if "recordsToDelete" in movimiento:
            ids_a_borrar = movimiento["recordsToDelete"]
            if ids_a_borrar:  # comprobamos que la lista no esté vacía
                cursor.executemany("DELETE FROM jugadores WHERE id = ?", [(id_val,) for id_val in ids_a_borrar])
                print(f"🗑️ Borrados {len(ids_a_borrar)} jugadores")

        # 🟢 Insertar registros
        if "recordsToInsert" in movimiento:
            jugadores_a_insertar = movimiento["recordsToInsert"]
            if jugadores_a_insertar:
                for jugador in jugadores_a_insertar:
                    cursor.execute("""
                        INSERT INTO jugadores (nombre, posicion, equipo, valor, usuario_id)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        jugador.get("nombre"),
                        jugador.get("posicion", None),
                        jugador.get("equipo"),
                        jugador.get("valor", 0),        # valor por defecto si no existe
                        jugador.get("usuario_id", None) # puede ser null
                    ))
                print(f"✅ Insertados {len(jugadores_a_insertar)} jugadores")

    conn.commit()

def insertar_historial_usuarios(conn):
    users_bbdd = obtener_registros_tabla(conn, 'usuarios', ['id', 'name', 'url_name', 'saldo', 'num_jugadores', 'modificationDate'])
    historial_list = []
    for user in users_bbdd:
        historial_to_insert = {'usuario_id': user['id'], 'saldo': user['saldo'], 'num_jugadores': user['num_jugadores'], 'modificationDate': user['modificationDate']}
        historial_list.append(historial_to_insert)

    insertar_varios(conn, 'usuarios_historial', historial_list)
