from flask import Flask, request, jsonify, render_template, redirect, url_for
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# Banco via variável de ambiente no Render
DB_URL = os.environ.get("postgres://meu_banco_usuarios_user:QizBCn2FYsshLhzmJi4jjghKgwvJph0F@dpg-d1amct15pdvs73b0c48g-a:5432/meu_banco_usuarios")

def get_conn():
    return psycopg2.connect(DB_URL)

def inicializar_banco():
    with get_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    usuario TEXT UNIQUE NOT NULL,
                    senha TEXT NOT NULL
                )
            """)
            # Cria usuário admin se não existir
            cursor.execute("SELECT 1 FROM usuarios WHERE usuario='admin'")
            if cursor.fetchone() is None:
                cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (%s, %s)", ("admin", "1234"))
        conn.commit()

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    usuario = data.get("user")
    senha = data.get("pass")
    with get_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM usuarios WHERE usuario=%s AND senha=%s", (usuario, senha))
            valid = cursor.fetchone() is not None
    return jsonify({"valid": valid})

@app.route("/")
def index():
    with get_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, usuario FROM usuarios ORDER BY id")
            usuarios = cursor.fetchall()
    return render_template("index.html", usuarios=usuarios)

@app.route("/adicionar", methods=["POST"])
def adicionar():
    usuario = request.form.get("usuario")
    senha = request.form.get("senha")
    if usuario and senha:
        try:
            with get_conn() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (%s, %s)", (usuario, senha))
                conn.commit()
        except Exception as e:
            print(f"Erro ao adicionar usuário: {e}")
    return redirect(url_for("index"))

@app.route("/remover/<int:user_id>")
def remover(user_id):
    with get_conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM usuarios WHERE id=%s", (user_id,))
        conn.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    inicializar_banco()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
