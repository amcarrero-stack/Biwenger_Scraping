from flask import Flask, jsonify, render_template
from flask_cors import CORS
import os
import psycopg
from psycopg.rows import dict_row

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()  # Supabase / Render (Postgres)

def _ensure_sslmode(url: str) -> str:
    # Si es una URL postgres y no tiene sslmode, añade ?sslmode=require
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://") and "sslmode=" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}sslmode=require"
    return url

def get_conn():
    """
    Devuelve una conexión a Postgres
    """
    url = _ensure_sslmode(DATABASE_URL)
    return psycopg.connect(url, row_factory=dict_row)

def fetch_all(sql: str, params: tuple | None = None):
    """
    Ejecuta un SELECT y devuelve lista de dicts
    """
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        rows = cur.fetchall()
        return rows
    finally:
        cur.close()
        conn.close()

# === Rutas API ===

@app.route("/api/usuarios")
def api_usuarios():
    usuarios = fetch_all("SELECT * FROM usuarios")
    return jsonify(usuarios)

@app.route("/api/jugadores/<int:usuario_id>")
def api_jugadores(usuario_id):
    sql = """
        SELECT *
        FROM jugadores
        WHERE usuario_id = %s
        ORDER BY 
            CASE posicion
                WHEN 'Portero' THEN 1
                WHEN 'Defensa' THEN 2
                WHEN 'Centrocampista' THEN 3
                WHEN 'Delantero' THEN 4
                ELSE 5
            END,
            nombre
    """
    jugadores = fetch_all(sql, (usuario_id,))
    return jsonify(jugadores)

@app.route("/api/movimientos/<int:usuario_id>")
def api_movimientos(usuario_id):
    sql = "SELECT * FROM movimientos WHERE usuario_id = %s ORDER BY fecha DESC"
    movimientos = fetch_all(sql, (usuario_id,))
    return jsonify(movimientos)

# Ruta web
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    import sys
    print("Running with: Postgres + psycopg3", file=sys.stderr)
    app.run(host="0.0.0.0", port=10000, debug=True)
