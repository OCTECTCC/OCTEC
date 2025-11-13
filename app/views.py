from flask import render_template, Blueprint, redirect, url_for, request, session, flash, jsonify, current_app
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash
from collections import defaultdict
from .models import *
from . import login_manager, db

from datetime import timezone, timedelta
try:
    from zoneinfo import ZoneInfo
    fuso_horario_disponivel = True
except Exception:
    ZoneInfo = None
    fuso_horario_disponivel = False

views = Blueprint("views", __name__)

@login_manager.user_loader
def load_user(id_usuario):
    if not id_usuario:
        return None
    
    if "-" in id_usuario:
        tipo, id = id_usuario.split("-", 1)

        try:
            id = int(id)
        except ValueError:
            return None
        
        if tipo == "aluno":
            return Alunos.query.get(id)
        elif tipo == "tec":
            return Tecnicos.query.get(id)
        elif tipo == "prof":
            return Professores.query.get(id)
        elif tipo == "coor":
            return Coordenadores.query.get(id)
        elif tipo == "dir":
            return Diretores.query.get(id)
        else:
            return None

    try:
        id = int(id_usuario)
    except ValueError:
        return None

    usuario = Diretores.query.get(id)
    if usuario:
        return usuario
    usuario = Coordenadores.query.get(id)
    if usuario:
        return usuario
    usuario = Professores.query.get(id)
    if usuario:
        return usuario
    usuario = Tecnicos.query.get(id)
    if usuario:
        return usuario
    return Alunos.query.get(id)

@views.route("/")
def index():
    if current_user.is_authenticated:
        tipo_usuario = current_user.id_cargo_usuario

        if tipo_usuario == 1:
            canais = Canais.query.filter_by(id_etec_canal=current_user.etec_aluno.id_etec).order_by(Canais.descricao_canal).all()

            if current_user.situacao_aluno == "CURSANDO":
                filtro_aulas = [
                    Aulas.modulo_aula == current_user.modulo_aluno,
                    Aulas.turma_aula.like(f"%{current_user.turma_aluno}%"),
                    Aulas.id_curso_aula == current_user.id_curso_aluno,
                    Aulas.id_etec_aula == current_user.id_etec_aluno
                ]                

                if current_user.curso_aluno.ensino_medio_integrado_curso == True:
                    if current_user.modulo_aluno in (1, 2):
                        ano_aula = current_user.ano_origem_aluno
                    elif current_user.modulo_aluno in (3, 4):
                        ano_aula = current_user.ano_origem_aluno + 1
                    elif current_user.modulo_aluno in (5, 6):
                        ano_aula = current_user.ano_origem_aluno + 2
                elif current_user.curso_aluno.ensino_medio_integrado_curso == False:
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
                        elif current_user.modulo_aluno == 4:
                            ano_aula = current_user.ano_origem_aluno + 2

                filtro_aulas.append(Aulas.ano_aula == ano_aula)
                aulas = Aulas.query.filter(*filtro_aulas).all()
                aulas_por_sala = None

        elif tipo_usuario == 2:
            canais = Canais.query.filter_by(id_etec_canal=current_user.etec_tec.id_etec).order_by(Canais.descricao_canal).all()
            aulas = None
            aulas_por_sala = None

        elif tipo_usuario == 3:
            canais = Canais.query.filter_by(id_etec_canal=current_user.etec_prof.id_etec).order_by(Canais.descricao_canal).all()
            
            aulas = Aulas.query.filter(
                Aulas.id_professor_aula == current_user.id_prof,
                Aulas.id_etec_aula == current_user.id_etec_prof
            ).all()

            grupos_aulas = defaultdict(list)

            for aula in aulas:
                if aula.curso_aula.ensino_medio_integrado_curso == True:
                    if aula.modulo_aula in (1,2):
                        serie_modulo = "1º"
                    elif aula.modulo_aula in (3,4):
                        serie_modulo = "2º"
                    elif aula.modulo_aula in (5,6):
                        serie_modulo = "3º"
                    descricao_aula = f"{serie_modulo} {aula.curso_aula.sigla_curso} {aula.ano_aula}"
                elif aula.curso_aula.ensino_medio_integrado_curso == False:
                    serie_modulo = f"{aula.modulo_aula}º MÓD."
                    descricao_aula = f"{serie_modulo} {aula.curso_aula.sigla_curso} {aula.ano_aula} {aula.semestre_aula}º SEM."
                
                grupos_aulas[descricao_aula].append(aula)

            aulas_por_sala = sorted(grupos_aulas.items(), key = lambda x: x[0])

        elif tipo_usuario == 4:
            canais = Canais.query.filter_by(id_etec_canal=current_user.etec_coor.id_etec).order_by(Canais.descricao_canal).all()

            aulas = Aulas.query.filter(
                Aulas.id_etec_aula == current_user.id_etec_coor
            ).all()

            grupos_aulas = defaultdict(list)

            if current_user.pedagogico_coor == True:
                for aula in aulas:
                    if aula.curso_aula.ensino_medio_integrado_curso == True:
                        if aula.modulo_aula in (1,2):
                            serie_modulo = "1º"
                        elif aula.modulo_aula in (3,4):
                            serie_modulo = "2º"
                        elif aula.modulo_aula in (5,6):
                            serie_modulo = "3º"
                        descricao_aula = f"{serie_modulo} {aula.curso_aula.sigla_curso} {aula.ano_aula}"
                    elif aula.curso_aula.ensino_medio_integrado_curso == False:
                        serie_modulo = f"{aula.modulo_aula}º MÓD."
                        descricao_aula = f"{serie_modulo} {aula.curso_aula.sigla_curso} {aula.ano_aula} {aula.semestre_aula}º SEM."
                    
                    grupos_aulas[descricao_aula].append(aula)
            else:
                if current_user.ensino_medio_coor == True:
                    for aula in aulas:
                        if aula.turma_aula == "AB":
                            if aula.curso_aula.ensino_medio_integrado_curso == True:
                                if aula.modulo_aula in (1,2):
                                    serie_modulo = "1º"
                                elif aula.modulo_aula in (3,4):
                                    serie_modulo = "2º"
                                elif aula.modulo_aula in (5,6):
                                    serie_modulo = "3º"
                                descricao_aula = f"{serie_modulo} {aula.curso_aula.sigla_curso} {aula.ano_aula}"
                            elif aula.curso_aula.ensino_medio_integrado_curso == False:
                                serie_modulo = f"{aula.modulo_aula}º MÓD."
                                descricao_aula = f"{serie_modulo} {aula.curso_aula.sigla_curso} {aula.ano_aula} {aula.semestre_aula}º SEM."
                            
                            grupos_aulas[descricao_aula].append(aula)

                for aula in aulas:
                    for curso in current_user.cursos_coor:
                        if aula.id_curso_aula == curso.id_curso and aula.turma_aula != "AB":
                            if aula.curso_aula.ensino_medio_integrado_curso == True:
                                if aula.modulo_aula in (1,2):
                                    serie_modulo = "1º"
                                elif aula.modulo_aula in (3,4):
                                    serie_modulo = "2º"
                                elif aula.modulo_aula in (5,6):
                                    serie_modulo = "3º"
                                descricao_aula = f"{serie_modulo} {aula.curso_aula.sigla_curso} {aula.ano_aula}"
                            elif aula.curso_aula.ensino_medio_integrado_curso == False:
                                serie_modulo = f"{aula.modulo_aula}º MÓD."
                                descricao_aula = f"{serie_modulo} {aula.curso_aula.sigla_curso} {aula.ano_aula} {aula.semestre_aula}º SEM."

                            grupos_aulas[descricao_aula].append(aula)

            aulas_por_sala = sorted(grupos_aulas.items(), key = lambda x: x[0])

        elif tipo_usuario == 5:
            canais = Canais.query.filter_by(id_etec_canal=current_user.etec_dir.id_etec).order_by(Canais.descricao_canal).all()
            
            aulas = Aulas.query.filter(
                Aulas.id_etec_aula == current_user.id_etec_dir
            ).all()

            grupos_aulas = defaultdict(list)

            for aula in aulas:
                if aula.curso_aula.ensino_medio_integrado_curso == True:
                    if aula.modulo_aula in (1,2):
                        serie_modulo = "1º"
                    elif aula.modulo_aula in (3,4):
                        serie_modulo = "2º"
                    elif aula.modulo_aula in (5,6):
                        serie_modulo = "3º"
                    descricao_aula = f"{serie_modulo} {aula.curso_aula.sigla_curso} {aula.ano_aula}"
                elif aula.curso_aula.ensino_medio_integrado_curso == False:
                    serie_modulo = f"{aula.modulo_aula}º MÓD."
                    descricao_aula = f"{serie_modulo} {aula.curso_aula.sigla_curso} {aula.ano_aula} {aula.semestre_aula}º SEM."
                
                grupos_aulas[descricao_aula].append(aula)

            aulas_por_sala = sorted(grupos_aulas.items(), key = lambda x: x[0])

        return render_template("index.html", canais=canais, aulas=aulas, aulas_por_sala=aulas_por_sala)
        
    else:  
        return render_template("index.html")

def converter_fuso_horario(data_hora, fuso_horario="America/Sao_Paulo"):
    if not data_hora:
        return None

    if data_hora.tzinfo is None:
        data_hora = data_hora.replace(tzinfo=timezone.utc)
    
    try:
        if fuso_horario_disponivel:
            zona = ZoneInfo(fuso_horario)
        else:
            zona = timezone(timedelta(hours=-3))
        return data_hora.astimezone(zona).isoformat()
    except Exception:
        return data_hora.isoformat()

@views.route("/api/mensagens", methods=["GET"])
@login_required
def api_mensagens():
    tipo_chat = request.args.get("tipo_chat")
    id_chat = request.args.get("id_chat", type=int)

    if not tipo_chat or not id_chat:
        return jsonify([])
    
    if tipo_chat == "canal":
        mensagens = Mensagens.query.filter_by(id_canal_msg=id_chat).order_by(Mensagens.data_hora_msg.asc()).all()
    elif tipo_chat == "aula":
        mensagens = Mensagens.query.filter_by(id_aula_msg=id_chat).order_by(Mensagens.data_hora_msg.asc()).all()
    else:
        return jsonify([])

    res_msg = []

    for msg in mensagens:
        emissor_msg = {}

        if msg.aluno_msg:
            emissor_msg = {"tipo_usuario": "aluno", "id_usuario": msg.id_aluno_msg, "nome_usuario": msg.aluno_msg.nome_aluno}
        elif msg.prof_msg:
            emissor_msg = {"tipo_usuario": "prof", "id_usuario": msg.id_prof_msg, "nome_usuario": msg.prof_msg.nome_prof}
        elif msg.coor_msg:
            emissor_msg = {"tipo_usuario": "coor", "id_usuario": msg.id_coor_msg, "nome_usuario": msg.coor_msg.nome_coor}
        elif msg.dir_msg:
            emissor_msg = {"tipo_usuario": "dir", "id_usuario": msg.id_dir_msg, "nome_usuario": msg.dir_msg.nome_dir}

        res_msg.append({
            "id_msg": msg.id_msg,
            "texto_msg": msg.texto_msg,
            "data_hora_msg": converter_fuso_horario(msg.data_hora_msg),
            "emissor_msg": emissor_msg,
            "id_canal_msg": msg.id_canal_msg,
            "id_aula_msg": msg.id_aula_msg
        })
    
    return jsonify(res_msg)

@views.route("/api/mensagens/enviar", methods=["POST"])
@login_required
def api_enviar_mensagem():
    payload = request.get_json(force=True, silent=True) or request.form
    texto_msg = payload.get("texto_msg")
    tipo_chat = payload.get("tipo_chat")
    id_chat = payload.get("id_chat")

    if not texto_msg or not tipo_chat or not id_chat:
        return jsonify({"error": "Dados incompletos"}), 400
    
    texto_msg = texto_msg.strip()

    if len(texto_msg) == 0:
        return jsonify({"error": "Mensagem vazia"}), 400
    if len(texto_msg) > 200:
        return jsonify({"error": "Mensagem muito longa (máximo de 200 caracteres)"}), 400

    msg = Mensagens(texto_msg=texto_msg)

    try:
        id_chat = int(id_chat)
    except (TypeError, ValueError):
        return jsonify({"error": "ID inválido"}), 400
    
    if tipo_chat == "canal":
        msg.id_canal_msg = id_chat

        canal = Canais.query.get(id_chat)

        if not canal:
            return jsonify({"error": "Canal não encontrado"}), 404

        try:
            cargo_usuario = int(getattr(current_user, "id_cargo_usuario", None))
        except Exception:
            cargo_usuario = None
        
        if cargo_usuario is None or cargo_usuario < canal.id_cargo_emissor_canal:
            return jsonify({"error": "Você não tem permissão para enviar mensagens neste canal"}), 403

    elif tipo_chat == "aula":
        msg.id_aula_msg = id_chat
    else:
        return jsonify({"error": "Meio inválido"}), 400

    id_usuario_str = current_user.get_id()
    tipo_usuario = None
    id_usuario = None

    if id_usuario_str and "-" in id_usuario_str:
        tipo_usuario, id_usuario = id_usuario_str.split("-", 1)
        try:
            id_usuario = int(id_usuario)
        except:
            id_usuario = None
    else:
        if hasattr(current_user, "id_aluno"):
            tipo_usuario, id_usuario = "aluno", getattr(current_user, "id_aluno")
        elif hasattr(current_user, "id_prof"):
            tipo_usuario, id_usuario = "prof", getattr(current_user, "id_prof")
        elif hasattr(current_user, "id_coor"):
            tipo_usuario, id_usuario = "coor", getattr(current_user, "id_coor")
        elif hasattr(current_user, "id_dir"):
            tipo_usuario, id_usuario = "dir", getattr(current_user, "id_dir")
    
    if tipo_usuario == "aluno":
        msg.id_aluno_msg = id_usuario
    elif tipo_usuario == "prof":
        msg.id_prof_msg = id_usuario
    elif tipo_usuario == "coor":
        msg.id_coor_msg = id_usuario
    elif tipo_usuario == "dir":
        msg.id_dir_msg = id_usuario
    else:
        return jsonify({"error": "Usuário inválido"}), 400
    
    msg.data_hora_msg = func.now()

    db.session.add(msg)
    db.session.commit()

    msg = Mensagens.query.get(msg.id_msg)

    emissor_msg = {"tipo_usuario": tipo_usuario, "id_usuario": id_usuario}

    if tipo_usuario == "aluno":
        emissor_msg["nome_usuario"] = msg.aluno_msg.nome_aluno if msg.aluno_msg else None
    elif tipo_usuario == "prof":
        emissor_msg["nome_usuario"] = msg.prof_msg.nome_prof if msg.prof_msg else None
    elif tipo_usuario == "coor":
        emissor_msg["nome_usuario"] = msg.coor_msg.nome_coor if msg.coor_msg else None
    elif tipo_usuario == "dir":
        emissor_msg["nome_usuario"] = msg.dir_msg.nome_dir if msg.dir_msg else None

    return jsonify({
        "success": True,
        "id_msg": msg.id_msg,
        "texto_msg": msg.texto_msg,
        "data_hora_msg": converter_fuso_horario(msg.data_hora_msg),
        "emissor_msg": emissor_msg,
        "id_canal_msg": msg.id_canal_msg,
        "id_aula_msg": msg.id_aula_msg
    }), 201

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
                    login_user(aluno)
                    return redirect(url_for("views.index"))
                else:
                    flash("Usuário ou senha incorretos", "danger")
            else:
                flash("Usuário ou senha incorretos", "danger")

        elif tipo_usuario == 2:
            tecnico = Tecnicos.query.filter_by(login_tec=login_usuario).first()

            if tecnico:
                if etec.id_etec != tecnico.id_etec_tec:
                    flash("ETEC inválida", "danger")
                    return redirect(url_for("views.login"))

                if check_password_hash(tecnico.senha_tec, tecnico.cpf_tec) and senha_usuario == tecnico.cpf_tec:
                    session["session_tipo_usuario"] = tipo_usuario
                    session["session_login_usuario"] = login_usuario
                    return redirect(url_for("views.primeiro_acesso"))
                
                if check_password_hash(tecnico.senha_tec, senha_usuario):
                    login_user(tecnico)
                    return redirect(url_for("views.index"))  
                else:
                    flash("Usuário ou senha incorretos", "danger")
            else:
                flash("Usuário ou senha incorretos", "danger")

        elif tipo_usuario == 3:
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
                    login_user(professor)
                    return redirect(url_for("views.index"))  
                else:
                    flash("Usuário ou senha incorretos", "danger")
            else:
                flash("Usuário ou senha incorretos", "danger")

        elif tipo_usuario == 4:
            coordenador = Coordenadores.query.filter_by(login_coor=login_usuario).first()

            if coordenador:
                if etec.id_etec != coordenador.id_etec_coor:
                    flash("ETEC inválida", "danger")
                    return redirect(url_for("views.login"))

                if check_password_hash(coordenador.senha_coor, coordenador.cpf_coor) and senha_usuario == coordenador.cpf_coor:
                    session["session_tipo_usuario"] = tipo_usuario
                    session["session_login_usuario"] = login_usuario
                    return redirect(url_for("views.primeiro_acesso"))
                
                if check_password_hash(coordenador.senha_coor, senha_usuario):
                    login_user(coordenador)
                    return redirect(url_for("views.index"))  
                else:
                    flash("Usuário ou senha incorretos", "danger")
            else:
                flash("Usuário ou senha incorretos", "danger")

        elif tipo_usuario == 5:
            diretor = Diretores.query.filter_by(login_dir=login_usuario).first()

            if diretor:
                if etec.id_etec != diretor.id_etec_dir:
                    flash("ETEC inválida", "danger")
                    return redirect(url_for("views.login"))

                if check_password_hash(diretor.senha_dir, diretor.cpf_dir) and senha_usuario == diretor.cpf_dir:
                    session["session_tipo_usuario"] = tipo_usuario
                    session["session_login_usuario"] = login_usuario
                    return redirect(url_for("views.primeiro_acesso"))
                
                if check_password_hash(diretor.senha_dir, senha_usuario):
                    login_user(diretor)
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

@views.route("/perfil")
@login_required
def perfil():
    return render_template("perfil.html")

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
            tecnico = Tecnicos.query.filter_by(login_tec=login_usuario).first()

            if not tecnico:
                session.pop("session_tipo_usuario", None)
                session.pop("session_login_usuario", None)
                flash("Erro", "danger")
                return redirect(url_for("views.login"))

            tecnico.senha_tec = generate_password_hash(senha_usuario)
            db.session.commit()

            session.pop("session_tipo_usuario", None)
            session.pop("session_login_usuario", None)
            flash("Senha redefinida com sucesso!", "success")
            return redirect(url_for("views.login"))

        elif tipo_usuario == 3:
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

        elif tipo_usuario == 4:
            coordenador = Coordenadores.query.filter_by(login_coor=login_usuario).first()

            if not coordenador:
                session.pop("session_tipo_usuario", None)
                session.pop("session_login_usuario", None)
                flash("Erro", "danger")
                return redirect(url_for("views.login"))

            coordenador.senha_coor = generate_password_hash(senha_usuario)
            db.session.commit()

            session.pop("session_tipo_usuario", None)
            session.pop("session_login_usuario", None)
            flash("Senha redefinida com sucesso!", "success")
            return redirect(url_for("views.login"))

        elif tipo_usuario == 5:
            diretor = Diretores.query.filter_by(login_dir=login_usuario).first()

            if not diretor:
                session.pop("session_tipo_usuario", None)
                session.pop("session_login_usuario", None)
                flash("Erro", "danger")
                return redirect(url_for("views.login"))

            diretor.senha_dir = generate_password_hash(senha_usuario)
            db.session.commit()

            session.pop("session_tipo_usuario", None)
            session.pop("session_login_usuario", None)
            flash("Senha redefinida com sucesso!", "success")
            return redirect(url_for("views.login"))

    return render_template("primeiro_acesso.html", login_usuario=login_usuario)