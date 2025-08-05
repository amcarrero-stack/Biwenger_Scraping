import sqlite3
from pathlib import Path

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
            saldo REAL NOT NULL,
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
def insertar_usuario(conn, usuarios):
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