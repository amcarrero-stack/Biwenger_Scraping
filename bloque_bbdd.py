import os
import sqlite3
from pathlib import Path
from datetime import datetime
import locale
from utils import traducir_mes, log_message, log_message_with_print
import psycopg
from psycopg.rows import dict_row

locale.setlocale(locale.LC_TIME, "C")

# === Variable de entorno para Postgres (Render) ===
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

def get_db_connection():
    """
    Devuelve siempre conexión a Postgres usando psycopg (v3) con dict_row.
    """
    if not DATABASE_URL:
        raise RuntimeError("❌ DATABASE_URL no está definida en las variables de entorno.")
    try:
        # log_message_with_print("🔗 Conectando a Postgres...")
        print("🔗 Conectando a Postgres...")
        conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
        return conn
    except Exception as e:
        print(f"❌ Error al conectar a Postgres: {e}")
        # log_message_with_print(f"❌ Error al conectar a Postgres: {e}")
        raise

def cerrar_BBDD(conn):
    """
    Cierra la conexión a Postgres.
    """
    try:
        conn.close()
        # log_message_with_print("🔒 Conexión a Postgres cerrada.")
        print("🔒 Conexión a Postgres cerrada.")
    except Exception as e:
        # log_message_with_print(f"⚠️ Error cerrando conexión: {e}")
        print(f"⚠️ Error cerrando conexión: {e}")
def crear_tablas_si_no_existen(conn):
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            url_name TEXT UNIQUE NOT NULL,
            saldo BIGINT NOT NULL,
            saldo_anterior BIGINT NOT NULL,
            num_jugadores INTEGER,
            modificationDate TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios_historial (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
            saldo BIGINT NOT NULL,
            num_jugadores INTEGER,
            modificationDate TIMESTAMP,
            tipo_actualizacion TEXT CHECK(tipo_actualizacion IN ('delete', 'update', 'insert'))
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movimientos (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER REFERENCES usuarios(id),
            tipo TEXT CHECK(tipo IN ('fichaje', 'venta', 'clausulazo', 'abono', 'penalizacion', 'movimiento', 'cambioNombre')),
            jugador TEXT,
            cantidad BIGINT,
            fecha TIMESTAMP,
            accion TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jugadores (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER REFERENCES usuarios(id),
            nombre TEXT UNIQUE NOT NULL,
            valor BIGINT,
            posicion TEXT,
            equipo TEXT,
            href TEXT,
            modificationDate TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuario_jugador_historial (
            id SERIAL PRIMARY KEY,
            usuario_id INTEGER REFERENCES usuarios(id),
            jugador_id INTEGER REFERENCES jugadores(id),
            fecha TIMESTAMP
        )
    ''')

    conn.commit()
    cursor.close()

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
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (name, url_name) DO NOTHING
        ''', (name, url_name, saldo, saldo, num_jugadores, fecha_inicio_sql))
    conn.commit()

def obtener_userIds(conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, name FROM usuarios")
        usuarios = cursor.fetchall()  # [{'id': 1, 'name': 'Juan'}, {'id': 2, 'name': 'Pedro'}]

    # Crear diccionario: key = name, value = id
    user_dict = {row["name"]: row["id"] for row in usuarios}
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
    return {row["id"]: row["saldo"] for row in cursor.fetchall()}

def obtener_registros_tabla(conn, tabla, campos=None, where=None, orderby=None):
    cursor = conn.cursor()

    columnas = ", ".join(campos) if campos else "*"

    query = f"SELECT {columnas} FROM {tabla}"
    if where and where.strip():
        query += f" WHERE {where}"
    if orderby and orderby.strip():
        query += f" ORDER BY {orderby}"

    cursor.execute(query)
    registros = cursor.fetchall()  # ya devuelve lista de dicts

    cursor.close()
    return registros

def obtener_jugadores_dict(jugadores):
    # Diccionario: key = nombre, value = id
    return {jugador['nombre']: jugador['id'] for jugador in jugadores}

def actualizar_saldos_new(conn, nuevos_saldos):
    log_message_with_print("🌐 Actualizando los saldos...")
    cursor = conn.cursor()
    # Obtener la fecha actual en formato "5 ago 2025"
    fecha_hoy = datetime.today().replace(microsecond=0)
    saldos_actuales_by_userId = obtener_saldos(conn)

    # Normaliza a lista de tuplas (saldo, modificationDate, id)
    pares = [(int(saldo), fecha_hoy, int(saldos_actuales_by_userId[uid]), int(uid)) for uid, saldo in nuevos_saldos.items()]

    log_message('Pares en actualizar_saldos_new es:')
    log_message(pares)
    # Actualizamos saldo y modificationDate
    cursor.executemany(
        "UPDATE usuarios SET saldo = %s, modificationDate = %s, saldo_anterior = %s  WHERE id = %s",
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
    jugadores_bbdd = cursor.fetchall()  # con dict_row, devuelve [{'id': .., 'nombre': ..}, ...]
    jugador_dict = {jug['nombre']: jug['id'] for jug in jugadores_bbdd}

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
            "UPDATE usuarios SET num_jugadores = %s WHERE id = %s",
            (num_jug, usuario_id)
        )

        # Actualizamos el propietario de los jugadores
        for jugador_nombre in plantilla:
            if jugador_nombre in jugador_dict:
                jugador_id = jugador_dict[jugador_nombre]
                cursor.execute(
                    "UPDATE jugadores SET usuario_id = %s WHERE id = %s",
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
    Inserta un registro en la tabla de forma dinámica (Postgres).
    """
    campos = ", ".join(valores.keys())
    placeholders = ", ".join(["%s"] * len(valores))  # en Postgres es %s
    query = f"INSERT INTO {tabla} ({campos}) VALUES ({placeholders})"

    try:
        cursor = conn.cursor()
        cursor.execute(query, list(valores.values()))
        conn.commit()
        cursor.close()
        return True  # éxito
    except Exception as e:
        print(f"⚠️ Error insertando en {tabla}: {e} → {valores}")
        conn.rollback()
        return False

def insertar_varios(conn, tabla, lista_valores):
    # log_message_with_print("🌐 Insertando movimientos post...")
    """
    Inserta varios registros en la tabla a partir de una lista de diccionarios.
    """
    for item in lista_valores:
        insertar_registro(conn, tabla, item)

from datetime import datetime

def obtener_resumen_movimientos(conn, user_dict, fecha_inicio_str):
    log_message_with_print("🌐 Obteniendo resumen de los movimientos insertados...")
    cursor = conn.cursor()
    resultados = []
    fecha_hoy = datetime.today()

    for nombre, user_id in user_dict.items():
        resumen = {'usuario_id': user_id}

        # Ventas
        cursor.execute("""
            SELECT COALESCE(SUM(cantidad), 0) AS ventas
            FROM movimientos
            WHERE usuario_id = %s
              AND tipo = 'venta'
              AND fecha BETWEEN %s AND %s
        """, (user_id, fecha_inicio_str, fecha_hoy))
        resumen['ventas'] = cursor.fetchone()['ventas']

        # Fichajes
        cursor.execute("""
            SELECT COALESCE(SUM(cantidad), 0) AS fichajes
            FROM movimientos
            WHERE usuario_id = %s
              AND tipo = 'fichaje'
              AND fecha BETWEEN %s AND %s
        """, (user_id, fecha_inicio_str, fecha_hoy))
        resumen['fichajes'] = cursor.fetchone()['fichajes']

        # Penalizaciones
        cursor.execute("""
            SELECT COALESCE(SUM(cantidad), 0) AS penalizaciones
            FROM movimientos
            WHERE usuario_id = %s
              AND tipo = 'penalizacion'
              AND fecha BETWEEN %s AND %s
        """, (user_id, fecha_inicio_str, fecha_hoy))
        resumen['penalizaciones'] = cursor.fetchone()['penalizaciones']

        # Clausulazos
        cursor.execute("""
            SELECT COALESCE(SUM(cantidad), 0) AS clausulazos
            FROM movimientos
            WHERE usuario_id = %s
              AND tipo = 'clausulazo'
              AND fecha BETWEEN %s AND %s
        """, (user_id, fecha_inicio_str, fecha_hoy))
        resumen['clausulazos'] = cursor.fetchone()['clausulazos']

        # Abonos
        cursor.execute("""
            SELECT COALESCE(SUM(cantidad), 0) AS abonos
            FROM movimientos
            WHERE usuario_id = %s
              AND tipo = 'abono'
              AND fecha BETWEEN %s AND %s
        """, (user_id, fecha_inicio_str, fecha_hoy))
        resumen['abonos'] = cursor.fetchone()['abonos']

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
    Procesa los movimientos de jugadores: elimina, inserta y actualiza en la BBDD (Postgres).
    movimientos_jugadores: lista con diccionarios { "recordsToDelete": [...], "recordsToInsert": [...], "recordsToUpdate": [...] }
    conn: conexión a Postgres
    """
    cursor = conn.cursor()
    fecha_hoy = datetime.today().replace(microsecond=0)

    for movimiento in movimientos_jugadores:
        # 🔴 Borrar registros
        if "recordsToDelete" in movimiento:
            ids_a_borrar = movimiento["recordsToDelete"]
            if ids_a_borrar:  # comprobamos que la lista no esté vacía
                cursor.executemany(
                    "DELETE FROM jugadores WHERE id = %s",
                    [(id_val,) for id_val in ids_a_borrar]
                )
                print(f"🗑️ Borrados {len(ids_a_borrar)} jugadores")

        # 🟢 Insertar registros
        if "recordsToInsert" in movimiento:
            jugadores_a_insertar = movimiento["recordsToInsert"]
            if jugadores_a_insertar:
                for jugador in jugadores_a_insertar:
                    cursor.execute("""
                        INSERT INTO jugadores (nombre, posicion, equipo, valor, usuario_id, modificationDate)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        jugador.get("nombre"),
                        jugador.get("posicion", None),
                        jugador.get("equipo"),
                        jugador.get("valor", 0),         # valor por defecto si no existe
                        jugador.get("usuario_id", None), # puede ser null
                        fecha_hoy
                    ))
                print(f"✅ Insertados {len(jugadores_a_insertar)} jugadores")

        # 🔵 Actualizar registros
        if "recordsToUpdate" in movimiento:
            jugadores_a_actualizar = movimiento["recordsToUpdate"]
            if jugadores_a_actualizar:
                for jugador in jugadores_a_actualizar:
                    cursor.execute("""
                        UPDATE jugadores
                        SET nombre = %s, equipo = %s, modificationDate = %s
                        WHERE id = %s
                    """, (
                        jugador.get("nombre"),
                        jugador.get("equipo"),
                        fecha_hoy,
                        jugador.get("id")
                    ))
                print(f"🔄 Actualizados {len(jugadores_a_actualizar)} jugadores")

    conn.commit()


def insertar_historial_usuarios(conn):
    users_bbdd = obtener_registros_tabla(conn, 'usuarios', ['id', 'name', 'url_name', 'saldo', 'num_jugadores', 'modificationDate'])
    historial_list = []
    for user in users_bbdd:
        historial_to_insert = {'usuario_id': user['id'], 'saldo': user['saldo'], 'num_jugadores': user['num_jugadores'], 'modificationDate': user['modificationdate']}
        historial_list.append(historial_to_insert)

    insertar_varios(conn, 'usuarios_historial', historial_list)

# UTILIDADES A PARTIR DE AQUI

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

def delete_registros_table(conn, table):
    try:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table}")
        conn.commit()
        print(f"Todos los registros de {table} han sido eliminados.")
    except Exception as e:
        print(f"Error al borrar los movimientos {e}")

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

def agregar_campos(tabla, campos_dict, conn):
    """
    Agrega campos a una tabla de forma dinámica.
    :param tabla: str, nombre de la tabla
    :param campos_dict: dict, ejemplo {"modificationDate": "DATE", "otroCampo": "TEXT"}
    :param db_path: str, ruta de la base de datos
    """
    cursor = conn.cursor()

    for campo, tipo in campos_dict.items():
        sql = f"ALTER TABLE {tabla} ADD COLUMN {campo} {tipo}"
        try:
            cursor.execute(sql)
            print(f"Campo '{campo}' agregado correctamente a la tabla '{tabla}'")
        except sqlite3.OperationalError as e:
            print(f"No se pudo agregar el campo '{campo}': {e}")

    conn.commit()
