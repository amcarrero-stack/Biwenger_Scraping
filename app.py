from flask import Flask, jsonify, render_template
from flask_cors import CORS
import sqlite3
import os

# Crear app
app = Flask(__name__)
CORS(app)

# Ruta a la base de datos, se puede configurar vía variable de entorno
DB_PATH = os.environ.get("DB_PATH", "BBDD/biwenger_bbdd.db")

def get_conn():
    return sqlite3.connect(DB_PATH)

# Rutas API
@app.route("/api/usuarios")
def api_usuarios():
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios")
    usuarios = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(usuarios)

@app.route("/api/jugadores/<int:usuario_id>")
def api_jugadores(usuario_id):
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jugadores WHERE usuario_id = ?", (usuario_id,))
    jugadores = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(jugadores)

# Ruta web
@app.route("/")
def index():
    return render_template("index.html")

# Solo necesario para pruebas locales
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
