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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            url_name TEXT UNIQUE NOT NULL,
            saldo INTEGER NOT NULL,
            num_jugadores INTEGER,
            modificationDate TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            tipo TEXT CHECK(tipo IN ('fichaje', 'venta')),
            jugador TEXT,
            cantidad REAL,
            fecha TEXT
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
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios")
    conn.commit()
    print("Todos los usuarios han sido eliminados.")

# Consultar usuarios
def obtener_usuarios(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, saldo, url_name, num_jugadores, modificationDate FROM usuarios")
    usuarios = cursor.fetchall()
    return usuarios

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