from flask import render_template, Blueprint, redirect, url_for, request, session, flash, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from .models import *
from . import login_manager, db

views = Blueprint("views", __name__)

@login_manager.user_loader
def load_user(id_usuario):
    tipo_usuario = session.get("session_tipo_usuario")

    if tipo_usuario == 1:
        return Alunos.query.get(int(id_usuario))
    elif tipo_usuario == 2:
        return  Professores.query.get(int(id_usuario))
    else:
        return None

@views.route("/")
def index():
    if current_user.is_authenticated:
        canais = Canais.query.order_by(Canais.descricao_canal).all()

        tipo_usuario = current_user.id_cargo_usuario

        if tipo_usuario == 1:
            if current_user.situacao_aluno == "CURSANDO":
                filtro_aulas = [
                    Aulas.modulo_aula == current_user.modulo_aluno,
                    Aulas.turma_aula.like(f"%{current_user.turma_aluno}%"),
                    Aulas.id_curso_aula == current_user.id_curso_aluno,
                    Aulas.id_etec_aula == current_user.id_etec_aluno
                ]                

                if current_user.curso_aluno.turno_curso in ("Manhã", "Integral", "Tarde"):
                    if current_user.modulo_aluno in (1, 2):
                        ano_aula = current_user.ano_origem_aluno
                    elif current_user.modulo_aluno in (3, 4):
                        ano_aula = current_user.ano_origem_aluno + 1
                    elif current_user.modulo_aluno in (5, 6):
                        ano_aula = current_user.ano_origem_aluno + 2
                elif current_user.curso_aluno.turno_curso == "Noturno":
                    if current_user.semestre_origem_aluno == 1:
                        if current_user.modulo_aluno in (1, 2):
                            ano_aula = current_user.ano_origem_aluno
                        elif current_user.modulo_aluno in (3, 4):
                            ano_aula = current_user.ano_origem_aluno + 1
                    elif current_user.semestre_origem_aluno == 2:
                        if current_user.modulo_aluno == 1:
                            ano_aula = current_user.ano_origem_aluno
                        elif current_user.modulo_aluno in (2, 3):
                            ano_aula = current_user.ano_origem_aluno + 1
                        elif current_user.modulo_aluno in (2, 3):
                            ano_aula = current_user.ano_origem_aluno + 2

                filtro_aulas.append(Aulas.ano_aula == ano_aula)
                aulas = Aulas.query.filter(*filtro_aulas).all()

        elif tipo_usuario == 2:
            aulas = Aulas.query.filter(
                Aulas.id_professor_aula == current_user.id_prof,
                Aulas.id_etec_aula == current_user.id_etec_prof
            ).all()

        return render_template("index.html", canais=canais, tipo_usuario=tipo_usuario, aulas=aulas)
        """
        if tipo_usuario == 1:
            if current_user.situacao_aluno == "CURSANDO":
                if current_user.curso_aluno.turno_curso == "Manhã" or current_user.curso_aluno.turno_curso == "Integral" or current_user.curso_aluno.turno_curso == "Tarde":
                    if current_user.modulo_aluno == 1 or current_user.modulo_aluno == 2:
                        aulas = Aulas.query.filter(
                            Aulas.modulo_aula == current_user.modulo_aluno,
                            Aulas.turma_aula.like(f"%{current_user.turma_aluno[0]}%"),
                            Aulas.ano_aula == current_user.ano_origem_aluno,
                            Aulas.id_curso_aula == current_user.id_curso_aluno,
                            Aulas.id_etec_aula == current_user.id_etec_aluno
                        ).all()
                    elif current_user.modulo_aluno == 3 or current_user.modulo_aluno == 4:
                        aulas = Aulas.query.filter(
                            Aulas.modulo_aula == current_user.modulo_aluno,
                            Aulas.turma_aula.like(f"%{current_user.turma_aluno[0]}%"),
                            Aulas.ano_aula == current_user.ano_origem_aluno + 1,
                            Aulas.id_curso_aula == current_user.id_curso_aluno,
                            Aulas.id_etec_aula == current_user.id_etec_aluno
                        ).all()
                    elif current_user.modulo_aluno == 5 or current_user.modulo_aluno == 6:
                        aulas = Aulas.query.filter(
                            Aulas.modulo_aula == current_user.modulo_aluno,
                            Aulas.turma_aula.like(f"%{current_user.turma_aluno[0]}%"),
                            Aulas.ano_aula == current_user.ano_origem_aluno + 2,
                            Aulas.id_curso_aula == current_user.id_curso_aluno,
                            Aulas.id_etec_aula == current_user.id_etec_aluno
                        ).all()
                elif current_user.curso_aluno.turno_curso == "Noturno":
                    if current_user.semestre_origem_aluno == 1:
                        if current_user.modulo_aluno == 1 or current_user.modulo_aluno == 2:
                            aulas = Aulas.query.filter(
                                Aulas.modulo_aula == current_user.modulo_aluno,
                                Aulas.turma_aula.like(f"%{current_user.turma_aluno[0]}%"),
                                Aulas.ano_aula == current_user.ano_origem_aluno,
                                Aulas.id_curso_aula == current_user.id_curso_aluno,
                                Aulas.id_etec_aula == current_user.id_etec_aluno
                            ).all()
                        elif current_user.modulo_aluno == 3 or current_user.modulo_aluno == 4:
                            aulas = Aulas.query.filter(
                                Aulas.modulo_aula == current_user.modulo_aluno,
                                Aulas.turma_aula.like(f"%{current_user.turma_aluno[0]}%"),
                                Aulas.ano_aula == current_user.ano_origem_aluno + 1,
                                Aulas.id_curso_aula == current_user.id_curso_aluno,
                                Aulas.id_etec_aula == current_user.id_etec_aluno
                            ).all()
                    elif current_user.semestre_origem_aluno == 2:
                        if current_user.modulo_aluno == 1:
                            aulas = Aulas.query.filter(
                                Aulas.modulo_aula == current_user.modulo_aluno,
                                Aulas.turma_aula.like(f"%{current_user.turma_aluno[0]}%"),
                                Aulas.ano_aula == current_user.ano_origem_aluno,
                                Aulas.id_curso_aula == current_user.id_curso_aluno,
                                Aulas.id_etec_aula == current_user.id_etec_aluno
                            ).all()
                        elif current_user.modulo_aluno == 2 or current_user.modulo_aluno == 3:
                            aulas = Aulas.query.filter(
                                Aulas.modulo_aula == current_user.modulo_aluno,
                                Aulas.turma_aula.like(f"%{current_user.turma_aluno[0]}%"),
                                Aulas.ano_aula == current_user.ano_origem_aluno + 1,
                                Aulas.id_curso_aula == current_user.id_curso_aluno,
                                Aulas.id_etec_aula == current_user.id_etec_aluno
                            ).all()
                        elif current_user.modulo_aluno == 4:
                            aulas = Aulas.query.filter(
                                Aulas.modulo_aula == current_user.modulo_aluno,
                                Aulas.turma_aula.like(f"%{current_user.turma_aluno[0]}%"),
                                Aulas.ano_aula == current_user.ano_origem_aluno + 2,
                                Aulas.id_curso_aula == current_user.id_curso_aluno,
                                Aulas.id_etec_aula == current_user.id_etec_aluno
                            ).all()
                return render_template("index.html", canais=canais, tipo_usuario=tipo_usuario, aulas=aulas)
        elif tipo_usuario == 2:
            aulas = Aulas.query.filter(
                Aulas.id_professor_aula == current_user.id_prof,
                Aulas.id_etec_aula == current_user.id_etec_prof
            ).all()
            return render_template("index.html", canais=canais, tipo_usuario=tipo_usuario, aulas=aulas)
        """
    else:  
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
                    session["session_tipo_usuario"] = tipo_usuario
                    session["session_login_usuario"] = login_usuario
                    return redirect(url_for("views.primeiro_acesso"))

                if check_password_hash(aluno.senha_aluno, senha_usuario):
                    session["session_tipo_usuario"] = tipo_usuario
                    login_user(aluno)
                    return redirect(url_for("views.index"))
                else:
                    flash("Usuário ou senha incorretos", "danger")
            else:
                flash("Usuário ou senha incorretos", "danger")

        elif tipo_usuario == 2:
            professor = Professores.query.filter_by(login_prof=login_usuario).first()

            if professor:
                if etec.id_etec != professor.id_etec_prof:
                    flash("ETEC inválida", "danger")
                    return redirect(url_for("views.login"))      

                if check_password_hash(professor.senha_prof, professor.cpf_prof) and senha_usuario == professor.cpf_prof:
                    session["session_tipo_usuario"] = tipo_usuario
                    session["session_login_usuario"] = login_usuario
                    return redirect(url_for("views.primeiro_acesso"))

                if check_password_hash(professor.senha_prof, senha_usuario):
                    session["session_tipo_usuario"] = tipo_usuario
                    login_user(professor)
                    return redirect(url_for("views.index"))  
                else:
                    flash("Usuário ou senha incorretos", "danger")
            else:
                flash("Usuário ou senha incorretos", "danger")

    session.pop("session_tipo_usuario", None)
    session.pop("session_login_usuario", None)    
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

@views.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("views.login"))

@views.route("/primeiro_acesso", methods=["GET","POST"])
def primeiro_acesso():
    if current_user.is_authenticated:
        return redirect(url_for("views.index"))

    tipo_usuario = session.get("session_tipo_usuario")
    login_usuario = session.get("session_login_usuario")

    if not tipo_usuario or not login_usuario:
        session.pop("session_tipo_usuario", None)
        session.pop("session_login_usuario", None)
        flash("Acesso não autorizado", "danger")
        return redirect(url_for("views.login"))
    
    if request.method == "POST":
        senha_usuario = request.form.get("senha_usuario")
        confirmar_senha_usuario = request.form.get("confirmar_senha_usuario")

        if senha_usuario != confirmar_senha_usuario:
            flash("As senhas não coincidem", "danger")
            return redirect(url_for("views.primeiro_acesso"))

        if tipo_usuario == 1:
            aluno = Alunos.query.filter_by(rm_aluno=login_usuario).first()

            if not aluno:
                session.pop("session_tipo_usuario", None)
                session.pop("session_login_usuario", None)
                flash("Erro", "danger")
                return redirect(url_for("views.login"))

            aluno.senha_aluno = generate_password_hash(senha_usuario)
            db.session.commit()

            session.pop("session_tipo_usuario", None)
            session.pop("session_login_usuario", None)
            flash("Senha redefinida com sucesso!", "success")
            return redirect(url_for("views.login"))

        elif tipo_usuario == 2:
            professor = Professores.query.filter_by(login_prof=login_usuario).first()

            if not professor:
                session.pop("session_tipo_usuario", None)
                session.pop("session_login_usuario", None)
                flash("Erro", "danger")
                return redirect(url_for("views.login"))

            professor.senha_prof = generate_password_hash(senha_usuario)
            db.session.commit()

            session.pop("session_tipo_usuario", None)
            session.pop("session_login_usuario", None)
            flash("Senha redefinida com sucesso!", "success")
            return redirect(url_for("views.login"))

    return render_template("primeiro_acesso.html", login_usuario=login_usuario)