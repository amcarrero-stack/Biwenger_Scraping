from flask import Flask, jsonify, render_template
from flask_cors import CORS
import os

# Intenta usar psycopg (psycopg 3). Asegúrate de tenerlo en requirements: psycopg[binary]
try:
    import psycopg
    from psycopg.rows import dict_row
    HAS_PSYCOPG = True
except Exception:
    HAS_PSYCOPG = False

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()  # Render (Postgres)

def _ensure_sslmode(url: str) -> str:
    # Si es una URL postgres y no tiene sslmode, añade ?sslmode=require
    if url.startswith("postgres://"):
        # Render suele dar "postgres://", conviértelo a "postgresql://"
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
    # Conexión psycopg3 con filas como dict
    return psycopg.connect(url, row_factory=dict_row)

def fetch_all(sql: str, params: tuple | None = None):
    """
    Ejecuta un SELECT y devuelve lista de dicts tanto en Postgres como en SQLite.
    """
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        rows = cur.fetchall()
        # En psycopg3 con dict_row ya son dicts; en sqlite rows son sqlite3.Row (mapeable a dict)
        if rows and not isinstance(rows[0], dict):
            rows = [dict(r) for r in rows]
        return rows
    finally:
        try:
            cur.close()
        except Exception:
            pass
        conn.close()

# === Rutas API ===

@app.route("/api/usuarios")
def api_usuarios():
    # Mismo SQL para ambos motores
    usuarios = fetch_all("SELECT * FROM usuarios")
    return jsonify(usuarios)

@app.route("/api/jugadores/<int:usuario_id>")
def api_jugadores(usuario_id):
    # Placeholders:
    # - psycopg usa %s internamente aunque aquí pasamos params y la lib adapta
    # - sqlite usa ? pero como ejecutamos con un único camino (fetch_all),
    #   manejamos dos SQLs según motor para evitar incompatibilidades.
    if DATABASE_URL and HAS_PSYCOPG:
        sql = "SELECT * FROM jugadores WHERE usuario_id = %s"
    else:
        sql = "SELECT * FROM jugadores WHERE usuario_id = ?"
    jugadores = fetch_all(sql, (usuario_id,))
    return jsonify(jugadores)

@app.route("/api/movimientos/<int:usuario_id>")
def api_movimientos(usuario_id):
    if DATABASE_URL and HAS_PSYCOPG:
        sql = "SELECT * FROM movimientos WHERE usuario_id = %s ORDER BY fecha DESC"
    else:
        sql = "SELECT * FROM movimientos WHERE usuario_id = ? ORDER BY fecha DESC"
    movimientos = fetch_all(sql, (usuario_id,))
    return jsonify(movimientos)

# Ruta web
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    import sys
    engine = "Postgres + psycopg3" if (DATABASE_URL and HAS_PSYCOPG) else "SQLite"
    print("Running with:", engine, file=sys.stderr)
    app.run(host="0.0.0.0", port=10000, debug=True)
