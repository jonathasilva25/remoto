from flask import Flask, request, jsonify, render_template, redirect
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)
USER_FILE = "usuarios.json"

# --- Carregar usuários ---
def carregar_usuarios():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w") as f:
            json.dump([], f)
    with open(USER_FILE) as f:
        return json.load(f)

# --- Salvar usuários ---
def salvar_usuarios(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

# --- Validação ---
def encontrar_usuario(nome):
    for u in carregar_usuarios():
        if u["usuario"] == nome:
            return u
    return None

# --- API de login com checagem de expiração ---
@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json
    usuario = data.get("user")
    senha = data.get("pass")
    u = encontrar_usuario(usuario)

    if u and u["senha"] == senha:
        expira_em = u.get("expira_em")
        if expira_em:
            expira_data = datetime.strptime(expira_em, "%Y-%m-%d %H:%M:%S")
            if datetime.now() > expira_data:
                return jsonify({"valid": False, "message": "Usuário expirado."})
        return jsonify({"valid": True})
    return jsonify({"valid": False})

# --- Interface de administração ---
@app.route("/")
def index():
    return render_template("index.html", usuarios=carregar_usuarios())

@app.route("/add", methods=["POST"])
def adicionar_usuario():
    nome = request.form["usuario"]
    senha = request.form["senha"]
    expira_em = request.form["expira_em"] or None
    if expira_em:
        try:
            datetime.strptime(expira_em, "%Y-%m-%d %H:%M:%S")  # valida formato
        except:
            return "Data inválida. Use YYYY-MM-DD HH:MM:SS", 400
    users = carregar_usuarios()
    if encontrar_usuario(nome):
        return "Usuário já existe", 400
    users.append({"usuario": nome, "senha": senha, "expira_em": expira_em})
    salvar_usuarios(users)
    return redirect("/")

@app.route("/remove/<usuario>")
def remover_usuario(usuario):
    users = carregar_usuarios()
    users = [u for u in users if u["usuario"] != usuario]
    salvar_usuarios(users)
    return redirect("/")

# --- Inicialização ---
if __name__ == "__main__":
    inicializar_banco()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
