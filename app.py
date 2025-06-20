from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_NAME = "usuarios.db"

# --- Inicializa o banco de dados se não existir ---
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
        # Adiciona um usuário padrão
        cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", ("admin", "1234"))
        conn.commit()
        conn.close()

# --- Rota para validar login ---
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    usuario = data.get("user")
    senha = data.get("pass")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE usuario=? AND senha=?", (usuario, senha))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"valid": True})
    else:
        return jsonify({"valid": False})

# --- Inicializa o app ---
if __name__ == "__main__":
    inicializar_banco()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
