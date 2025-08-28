from flask import Flask, jsonify, render_template
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

DB_PATH = "Biwenger_BBDD.sqlite"  # o la ruta a tu sqlite

def get_conn():
    return sqlite3.connect(DB_PATH)

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

@app.route("/")
def index():
    return render_template("index.html")
