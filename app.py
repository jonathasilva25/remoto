from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DB_NAME = "usuarios.db"

# --- Inicializa o banco se necessário ---
def inicializar_banco():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT NOT NULL UNIQUE,
                senha TEXT NOT NULL
            )
        """)
        cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", ("admin", "1234"))
        conn.commit()
        conn.close()

# --- API de login (usada pela aplicação desktop) ---
@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    usuario = data.get("user")
    senha = data.get("pass")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND senha=?", (usuario, senha))
    resultado = cursor.fetchone()
    conn.close()
    return jsonify({"valid": bool(resultado)})

# --- Painel Web para gerenciar usuários ---
@app.route("/")
def index():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, usuario FROM usuarios ORDER BY id")
    usuarios = cursor.fetchall()
    conn.close()
    return render_template("index.html", usuarios=usuarios)

@app.route("/adicionar", methods=["POST"])
def adicionar():
    usuario = request.form.get("usuario")
    senha = request.form.get("senha")
    if usuario and senha:
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", (usuario, senha))
            conn.commit()
        except:
            pass
        finally:
            conn.close()
    return redirect(url_for("index"))

@app.route("/remover/<int:user_id>")
def remover(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

# --- Inicialização ---
if __name__ == "__main__":
    inicializar_banco()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
