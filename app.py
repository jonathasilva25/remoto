from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3
import os
from datetime import datetime

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
                senha TEXT NOT NULL,
                expira_em TEXT
            )
        """)
        cursor.execute("INSERT INTO usuarios (usuario, senha, expira_em) VALUES (?, ?, ?)", ("admin", "1234", None))
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
    cursor.execute("SELECT expira_em FROM usuarios WHERE usuario=? AND senha=?", (usuario, senha))
    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        expira_em = resultado[0]
        if expira_em:
            try:
                expira_dt = datetime.strptime(expira_em, "%Y-%m-%d %H:%M")
                if datetime.now() > expira_dt:
                    return jsonify({"valid": False, "reason": "expired"})
            except:
                pass
        return jsonify({"valid": True})
    return jsonify({"valid": False})

# --- Painel Web para gerenciar usuários ---
@app.route("/")
def index():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, usuario, expira_em FROM usuarios ORDER BY id")
    usuarios = cursor.fetchall()
    conn.close()
    return render_template("index.html", usuarios=usuarios)

@app.route("/adicionar", methods=["POST"])
def adicionar():
    usuario = request.form.get("usuario")
    senha = request.form.get("senha")
    expira_em = request.form.get("expira_em") or None
    if usuario and senha:
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (usuario, senha, expira_em) VALUES (?, ?, ?)", (usuario, senha, expira_em))
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
