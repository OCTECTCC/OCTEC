from flask import render_template, Blueprint, redirect, url_for, request, session, flash, jsonify
from flask_login import current_user, login_user
from werkzeug.security import check_password_hash
from .models import *
from . import login_manager

views = Blueprint("views", __name__)

@login_manager.user_loader
def load_user(user_id):
    return None

@views.route("/")
def index():
    return render_template("index.html")

@views.route("/login", methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("views.index"))
    
    cidades = Cidades.query.order_by(Cidades.nome_cidade).all()
    etecs = Etecs.query.order_by(Etecs.nome_etec).all()
    cargos = Cargos.query.order_by(Cargos.id_cargo).all()

    if request.method == "POST":
        tipo_usuario = int(request.form.get("tipo_usuario"))
        etec_usuario = request.form.get("etec_usuario")
        login_usuario = request.form.get("login_usuario")
        senha_usuario = request.form.get("senha_usuario")

        etec = Etecs.query.filter_by(codigo_etec=etec_usuario).first()

        if not etec:
            flash("ETEC inexistente", "danger")
            return redirect(url_for("views.login"))

        if tipo_usuario == 1:
            aluno = Alunos.query.filter_by(rm_aluno=login_usuario).first()

            if aluno:
                if etec.id_etec != aluno.id_etec_aluno:
                    flash("ETEC inválida", "danger")
                    return redirect(url_for("views.login"))

                if check_password_hash(aluno.senha_aluno, aluno.cpf_aluno) and senha_usuario == aluno.cpf_aluno:
                    return redirect(url_for("views.primeiro_acesso"))

                if check_password_hash(aluno.senha_aluno, senha_usuario):
                    login_user(aluno)
                    return redirect(url_for("views.index"))
                else:
                    flash("Usuário ou senha incorretos", "danger")
            else:
                flash("RM inválido", "danger")

        elif tipo_usuario == 2:
            professor = Professores.query.filter_by(login_prof=login_usuario).first()

            if professor:
                if etec.id_etec != professor.id_etec_prof:
                    flash("ETEC inválida", "danger")
                    return redirect(url_for("views.login"))      

                if check_password_hash(professor.senha_prof, professor.cpf_prof) and senha_usuario == professor.cpf_prof:
                    return redirect(url_for("views.primeiro_acesso"))

                if check_password_hash(professor.senha_prof, senha_usuario):
                    login_user(professor)
                    return redirect(url_for("views.index"))  
                else:
                    flash("Usuário ou senha incorretos", "danger")
            else:
                flash("Login inválido", "danger") 
                
        elif tipo_usuario == 3:
            administrador = Administradores.query.filter_by(login_adm=login_usuario).first()

            if administrador:
                if etec.id_etec != administrador.id_etec_adm:
                    flash("ETEC inválida", "danger")
                    return redirect(url_for("views.login"))                
                
                if check_password_hash(administrador.senha_adm, administrador.cpf_adm) and senha_usuario == administrador.cpf_adm:
                    return redirect(url_for("views.primeiro_acesso"))

                if check_password_hash(administrador.senha_adm, senha_usuario):
                    login_user(administrador)
                    return redirect(url_for("views.index")) 
                else:
                    flash("Usuário ou senha incorretos", "danger")
            else:
                flash("Login inválido", "danger") 
                
    return render_template("login.html", cargos=cargos, cidades=cidades, etecs=etecs)

@views.route("/api/etecs")
def etecs_por_cidade():
    id_cidade = request.args.get("cidade", type=int)

    if not id_cidade:
        return jsonify([])

    etecs = Etecs.query.filter_by(id_cidade_etec=id_cidade).order_by(Etecs.nome_etec).all()

    resultado = [
        {
            "id_etec": etec.id_etec,
            "codigo_etec": etec.codigo_etec,
            "nome_etec": etec.nome_etec
        }
        for etec in etecs
    ]
    return jsonify(resultado)

@views.route("/primeiro_acesso")
def primeiro_acesso():    
    return render_template("primeiro_acesso.html")