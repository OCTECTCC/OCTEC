import re
from . import db
from datetime import timezone, timedelta
from collections import defaultdict
from flask import render_template, Blueprint, redirect, url_for, request, session, flash, jsonify, current_app, abort
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash
from .models import *

try:
    from zoneinfo import ZoneInfo
    fuso_horario_disponivel = True
except Exception:
    ZoneInfo = None
    fuso_horario_disponivel = False

views = Blueprint("views", __name__)

@views.route("/")
def index():
    canais = []
    aulas = None
    aulas_por_sala = []

    if current_user.is_authenticated:
        tipo_usuario = getattr(current_user, "id_cargo_usuario", None)

        if tipo_usuario == 1:
            canais = Canais.query.filter_by(id_etec_canal=current_user.etec_aluno.id_etec).order_by(Canais.descricao_canal).all()

            if getattr(current_user, "situacao_aluno", None) == "CURSANDO":
                filtro_aulas = [
                    Aulas.modulo_aula == current_user.modulo_aluno,
                    Aulas.turma_aula.like(f"%{current_user.turma_aluno}%"),
                    Aulas.id_curso_aula == current_user.id_curso_aluno,
                    Aulas.id_etec_aula == current_user.id_etec_aluno
                ]                

                ano_aula = None

                try:
                    if current_user.curso_aluno.ensino_medio_integrado_curso:
                        if current_user.modulo_aluno in (1, 2):
                            ano_aula = current_user.ano_origem_aluno
                        elif current_user.modulo_aluno in (3, 4):
                            ano_aula = current_user.ano_origem_aluno + 1
                        elif current_user.modulo_aluno in (5, 6):
                            ano_aula = current_user.ano_origem_aluno + 2
                    else:
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
                except Exception:
                    ano_aula = None

                if ano_aula is not None:
                    filtro_aulas.append(Aulas.ano_aula == ano_aula)
                    aulas = Aulas.query.filter(*filtro_aulas).all()
                else:
                    aulas = []

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
                if aula.curso_aula.ensino_medio_integrado_curso:
                    if aula.modulo_aula in (1, 2):
                        serie_modulo = "1º"
                    elif aula.modulo_aula in (3, 4):
                        serie_modulo = "2º"
                    elif aula.modulo_aula in (5, 6):
                        serie_modulo = "3º"

                    descricao_aula = f"{serie_modulo} {aula.curso_aula.sigla_curso} {aula.ano_aula}"
                else:
                    serie_modulo = f"{aula.modulo_aula}º MÓD."
                    descricao_aula = f"{serie_modulo} {aula.curso_aula.sigla_curso} {aula.ano_aula} {aula.semestre_aula}º SEM."
                
                grupos_aulas[descricao_aula].append(aula)

            aulas_por_sala = sorted(grupos_aulas.items(), key=lambda x: x[0])

        elif tipo_usuario == 4:
            canais = Canais.query.filter_by(id_etec_canal=current_user.etec_coor.id_etec).order_by(Canais.descricao_canal).all()

            aulas = Aulas.query.filter(
                Aulas.id_etec_aula == current_user.id_etec_coor
            ).all()

            grupos_aulas = defaultdict(list)

            if getattr(current_user, "pedagogico_coor", False):
                for aula in aulas:
                    if aula.curso_aula.ensino_medio_integrado_curso:
                        if aula.modulo_aula in (1, 2):
                            serie_modulo = "1º"
                        elif aula.modulo_aula in (3, 4):
                            serie_modulo = "2º"
                        elif aula.modulo_aula in (5, 6):
                            serie_modulo = "3º"

                        descricao_aula = f"{serie_modulo} {aula.curso_aula.sigla_curso} {aula.ano_aula}"
                    elif aula.curso_aula.ensino_medio_integrado_curso == False:
                        serie_modulo = f"{aula.modulo_aula}º MÓD."
                        descricao_aula = f"{serie_modulo} {aula.curso_aula.sigla_curso} {aula.ano_aula} {aula.semestre_aula}º SEM."
                    
                    grupos_aulas[descricao_aula].append(aula)
            else:
                if getattr(current_user, "ensino_medio_coor", False):
                    for aula in aulas:
                        if aula.turma_aula == "AB":
                            if aula.curso_aula.ensino_medio_integrado_curso:
                                if aula.modulo_aula in (1, 2):
                                    serie_modulo = "1º"
                                elif aula.modulo_aula in (3, 4):
                                    serie_modulo = "2º"
                                elif aula.modulo_aula in (5, 6):
                                    serie_modulo = "3º"
                                    
                                descricao_aula = f"{serie_modulo} {aula.curso_aula.sigla_curso} {aula.ano_aula}"
                            else:
                                serie_modulo = f"{aula.modulo_aula}º MÓD."
                                descricao_aula = f"{serie_modulo} {aula.curso_aula.sigla_curso} {aula.ano_aula} {aula.semestre_aula}º SEM."
                            
                            grupos_aulas[descricao_aula].append(aula)

                for aula in aulas:
                    for curso in current_user.cursos_coor:
                        if aula.id_curso_aula == curso.id_curso and aula.turma_aula != "AB":
                            if aula.curso_aula.ensino_medio_integrado_curso:
                                if aula.modulo_aula in (1, 2):
                                    serie_modulo = "1º"
                                elif aula.modulo_aula in (3, 4):
                                    serie_modulo = "2º"
                                elif aula.modulo_aula in (5, 6):
                                    serie_modulo = "3º"

                                descricao_aula = f"{serie_modulo} {aula.curso_aula.sigla_curso} {aula.ano_aula}"
                            else:
                                serie_modulo = f"{aula.modulo_aula}º MÓD."
                                descricao_aula = f"{serie_modulo} {aula.curso_aula.sigla_curso} {aula.ano_aula} {aula.semestre_aula}º SEM."

                            grupos_aulas[descricao_aula].append(aula)

            aulas_por_sala = sorted(grupos_aulas.items(), key=lambda x: x[0])

        elif tipo_usuario == 5:
            canais = Canais.query.filter_by(id_etec_canal=current_user.etec_dir.id_etec).order_by(Canais.descricao_canal).all()
            
            aulas = Aulas.query.filter(
                Aulas.id_etec_aula == current_user.id_etec_dir
            ).all()

            grupos_aulas = defaultdict(list)

            for aula in aulas:
                if aula.curso_aula.ensino_medio_integrado_curso:
                    if aula.modulo_aula in (1, 2):
                        serie_modulo = "1º"
                    elif aula.modulo_aula in (3, 4):
                        serie_modulo = "2º"
                    elif aula.modulo_aula in (5, 6):
                        serie_modulo = "3º"

                    descricao_aula = f"{serie_modulo} {aula.curso_aula.sigla_curso} {aula.ano_aula}"
                else:
                    serie_modulo = f"{aula.modulo_aula}º MÓD."
                    descricao_aula = f"{serie_modulo} {aula.curso_aula.sigla_curso} {aula.ano_aula} {aula.semestre_aula}º SEM."
                
                grupos_aulas[descricao_aula].append(aula)

            aulas_por_sala = sorted(grupos_aulas.items(), key=lambda x: x[0])

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

def rotulo_emissor(tipo_usuario, usuario):
    if not usuario:
        return None
    
    if tipo_usuario == "aluno":
        return getattr(usuario, "nome_aluno", None)

    if tipo_usuario == "tec":
        nome = getattr(usuario, "nome_tec", None)
        sexo = getattr(usuario, "sexo_tec", None)
        cargo = "Técnico" if sexo == "M" else "Técnica"
        return f"{cargo} {nome}" if nome else None

    if tipo_usuario == "prof":
        nome = getattr(usuario, "nome_prof", None)
        sexo = getattr(usuario, "sexo_prof", None)
        cargo = "Professor" if sexo == "M" else "Professora"
        return f"{cargo} {nome}" if nome else None

    if tipo_usuario == "coor":
        nome = getattr(usuario, "nome_coor", None)
        sexo = getattr(usuario, "sexo_coor", None)
        cargo = "Coordenador" if sexo == "M" else "Coordenadora"
        return f"{cargo} {nome}" if nome else None

    if tipo_usuario == "dir":
        nome = getattr(usuario, "nome_dir", None)
        sexo = getattr(usuario, "sexo_dir", None)
        cargo = "Diretor" if sexo == "M" else "Diretora"
        return f"{cargo} {nome}" if nome else None

    return None

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
            emissor_msg["tipo_usuario"] = "aluno"
            emissor_msg["id_usuario"] = msg.id_aluno_msg
            emissor_msg["nome_usuario"] = msg.aluno_msg.nome_aluno
            emissor_msg["rotulo_emissor"] = rotulo_emissor("aluno", msg.aluno_msg)
            emissor_msg["representante"] = bool(getattr(msg.aluno_msg, "representante_aluno", False))
        elif msg.tec_msg:
            emissor_msg["tipo_usuario"] = "tec"
            emissor_msg["id_usuario"] = msg.id_tec_msg
            emissor_msg["nome_usuario"] = msg.tec_msg.nome_tec
            emissor_msg["rotulo_emissor"] = rotulo_emissor("tec", msg.tec_msg)
            emissor_msg["representante"] = False
        elif msg.prof_msg:
            emissor_msg["tipo_usuario"] = "prof"
            emissor_msg["id_usuario"] = msg.id_prof_msg
            emissor_msg["nome_usuario"] = msg.prof_msg.nome_prof
            emissor_msg["rotulo_emissor"] = rotulo_emissor("prof", msg.prof_msg)
            emissor_msg["representante"] = False
        elif msg.coor_msg:
            emissor_msg["tipo_usuario"] = "coor"
            emissor_msg["id_usuario"] = msg.id_coor_msg
            emissor_msg["nome_usuario"] = msg.coor_msg.nome_coor
            emissor_msg["rotulo_emissor"] = rotulo_emissor("coor", msg.coor_msg)
            emissor_msg["representante"] = False
        elif msg.dir_msg:
            emissor_msg["tipo_usuario"] = "dir"
            emissor_msg["id_usuario"] = msg.id_dir_msg
            emissor_msg["nome_usuario"] = msg.dir_msg.nome_dir
            emissor_msg["rotulo_emissor"] = rotulo_emissor("dir", msg.dir_msg)
            emissor_msg["representante"] = False

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
    payload = request.get_json(silent=True) or request.form or {}
    texto_msg = payload.get("texto_msg")
    tipo_chat = payload.get("tipo_chat")
    id_chat = payload.get("id_chat")

    if not texto_msg or not tipo_chat or not id_chat:
        return jsonify({"error": "Dados incompletos"}), 400
    
    texto_msg = str(texto_msg).strip()

    if len(texto_msg) == 0:
        return jsonify({"error": "Mensagem vazia"}), 400
    
    if len(texto_msg) > 200:
        return jsonify({"error": "Mensagem muito longa (máximo de 200 caracteres)"}), 400

    try:
        id_chat = int(id_chat)
    except (TypeError, ValueError):
        return jsonify({"error": "ID inválido"}), 400
    
    msg = Mensagens(texto_msg=texto_msg)
    
    if tipo_chat == "canal":
        msg.id_canal_msg = id_chat
        canal = Canais.query.get(id_chat)

        if not canal:
            return jsonify({"error": "Canal não encontrado"}), 404

        try:
            cargo_usuario = int(getattr(current_user, "id_cargo_usuario", None))
        except Exception:
            cargo_usuario = None
        
        cargo_emissor = getattr(canal, "id_cargo_emissor_canal", None)
        cargo_moderador = getattr(canal, "id_cargo_moderador_canal", None)

        permitido = False

        try:
            if cargo_usuario is None:
                permitido = False
            else:
                if cargo_emissor is not None and cargo_usuario >= cargo_emissor:
                    permitido = True
                elif cargo_moderador is not None and cargo_usuario == cargo_moderador:
                    permitido = True
                else:
                    permitido = False
        except Exception:
            permitido = False

        if not permitido:
            return jsonify({"error": "Você não tem permissão para enviar mensagens neste canal"}), 403

    elif tipo_chat == "aula":
        msg.id_aula_msg = id_chat
    else:
        return jsonify({"error": "Meio inválido"}), 400

    id_usuario_str = current_user.get_id()
    tipo_usuario = None
    id_usuario = None

    if id_usuario_str and "-" in id_usuario_str:
        tipo_usuario, id_usuario_bruto = id_usuario_str.split("-", 1)
        try:
            id_usuario = int(id_usuario_bruto)
        except:
            id_usuario = None
    else:
        if hasattr(current_user, "id_aluno"):
            tipo_usuario, id_usuario = "aluno", getattr(current_user, "id_aluno")
        elif hasattr(current_user, "id_tec"):
            tipo_usuario, id_usuario = "tec", getattr(current_user, "id_tec")
        elif hasattr(current_user, "id_prof"):
            tipo_usuario, id_usuario = "prof", getattr(current_user, "id_prof")
        elif hasattr(current_user, "id_coor"):
            tipo_usuario, id_usuario = "coor", getattr(current_user, "id_coor")
        elif hasattr(current_user, "id_dir"):
            tipo_usuario, id_usuario = "dir", getattr(current_user, "id_dir")
    
    if tipo_usuario == "aluno":
        msg.id_aluno_msg = id_usuario
    elif tipo_usuario == "tec":
        msg.id_tec_msg = id_usuario
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
        emissor_msg["rotulo_emissor"] = rotulo_emissor("aluno", msg.aluno_msg) if msg.aluno_msg else None
    elif tipo_usuario == "tec":
        emissor_msg["nome_usuario"] = msg.tec_msg.nome_tec if msg.tec_msg else None
        emissor_msg["rotulo_emissor"] = rotulo_emissor("tec", msg.tec_msg) if msg.tec_msg else None
    elif tipo_usuario == "prof":
        emissor_msg["nome_usuario"] = msg.prof_msg.nome_prof if msg.prof_msg else None
        emissor_msg["rotulo_emissor"] = rotulo_emissor("prof", msg.prof_msg) if msg.prof_msg else None
    elif tipo_usuario == "coor":
        emissor_msg["nome_usuario"] = msg.coor_msg.nome_coor if msg.coor_msg else None
        emissor_msg["rotulo_emissor"] = rotulo_emissor("coor", msg.coor_msg) if msg.coor_msg else None
    elif tipo_usuario == "dir":
        emissor_msg["nome_usuario"] = msg.dir_msg.nome_dir if msg.dir_msg else None
        emissor_msg["rotulo_emissor"] = rotulo_emissor("dir", msg.dir_msg) if msg.dir_msg else None

    return jsonify({
        "success": True,
        "id_msg": msg.id_msg,
        "texto_msg": msg.texto_msg,
        "data_hora_msg": converter_fuso_horario(msg.data_hora_msg),
        "emissor_msg": emissor_msg,
        "id_canal_msg": msg.id_canal_msg,
        "id_aula_msg": msg.id_aula_msg
    }), 201

@views.route("/api/mensagens/excluir", methods=["POST"])
@login_required
def api_excluir_mensagem():
    payload = request.get_json(silent=True) or request.form.to_dict() or {}
    id_msg_bruto = payload.get("id_msg") or payload.get("idMensagem") or payload.get("id")

    try:
        id_msg = int(id_msg_bruto)
    except Exception:
        return jsonify({"error": "ID da mensagem inválido"}), 400

    msg = Mensagens.query.get(id_msg)

    if not msg:
        return jsonify({"error": "Mensagem não encontrada"}), 404
    
    id_usuario_str = current_user.get_id() if hasattr(current_user, "get_id") else None
    tipo_usuario_atual = None
    id_usuario_atual = None

    if id_usuario_str and "-" in id_usuario_str:
        tipo_usuario_atual, id_usuario_bruto = id_usuario_str.split("-", 1)

        try:
            id_usuario_atual = int(id_usuario_bruto)
        except:
            id_usuario_atual = None
    else:
        if hasattr(current_user, "id_aluno"):
            tipo_usuario_atual, id_usuario_atual = "aluno", getattr(current_user, "id_aluno")
        elif hasattr(current_user, "id_tec"):
            tipo_usuario_atual, id_usuario_atual = "tec", getattr(current_user, "id_tec")
        elif hasattr(current_user, "id_prof"):
            tipo_usuario_atual, id_usuario_atual = "prof", getattr(current_user, "id_prof")
        elif hasattr(current_user, "id_coor"):
            tipo_usuario_atual, id_usuario_atual = "coor", getattr(current_user, "id_coor")
        elif hasattr(current_user, "id_dir"):
            tipo_usuario_atual, id_usuario_atual = "dir", getattr(current_user, "id_dir")

    emissor_tipo = None
    emissor_obj = None

    if msg.aluno_msg:
        emissor_tipo = "aluno"
        emissor_obj = msg.aluno_msg
    elif msg.tec_msg:
        emissor_tipo = "tec"
        emissor_obj = msg.tec_msg
    elif msg.prof_msg:
        emissor_tipo = "prof"
        emissor_obj = msg.prof_msg
    elif msg.coor_msg:
        emissor_tipo = "coor"
        emissor_obj = msg.coor_msg
    elif msg.dir_msg:
        emissor_tipo = "dir"
        emissor_obj = msg.dir_msg

    pertence = False

    try:
        if tipo_usuario_atual == "aluno" and msg.id_aluno_msg == id_usuario_atual:
            pertence = True
        elif tipo_usuario_atual == "tec" and msg.id_tec_msg == id_usuario_atual:
            pertence = True
        elif tipo_usuario_atual == "prof" and msg.id_prof_msg == id_usuario_atual:
            pertence = True
        elif tipo_usuario_atual == "coor" and msg.id_coor_msg == id_usuario_atual:
            pertence = True
        elif tipo_usuario_atual == "dir" and msg.id_dir_msg == id_usuario_atual:
            pertence = True
    except Exception:
        pertence = False

    if pertence:
        try:
            db.session.delete(msg)
            db.session.commit()
            return jsonify({"success": True})
        except Exception as exception:
            current_app.logger.exception("Erro ao excluir mensagem (id=%s): %s", id_msg, str(exception))
            db.session.rollback()
            return jsonify({"error": "Erro interno ao excluir mensagem", "detail": str(exception)}), 500
        
    tipo_aula = msg.id_aula_msg is not None
    tipo_canal = msg.id_canal_msg is not None

    if not (tipo_aula or tipo_canal):
        return jsonify({"error": "Você não tem permissão para excluir esta mensagem"}), 403

    try:
        cargo_atual = int(getattr(current_user, "id_cargo_usuario", 0))
    except Exception:
        cargo_atual = 0

    emissor_representante = False

    if emissor_tipo == "aluno" and emissor_obj is not None:
        emissor_representante = bool(getattr(emissor_obj, "representante_aluno", False))

    permitido = False

    try:
        if cargo_atual == 1:
            if getattr(current_user, "representante_aluno", False) and emissor_tipo == "aluno" and emissor_representante == False:
                permitido = True
        elif cargo_atual == 3:
            if emissor_tipo == "aluno":
                permitido = True
        elif cargo_atual == 4:
            if emissor_tipo in ("aluno", "prof"):
                permitido = True
        elif cargo_atual == 5:
            permitido = True
        else:
            permitido = False
    except Exception:
        permitido = False

    if not permitido:
        return jsonify({"error": "Você não tem permissão para excluir esta mensagem"}), 403

    try:
        db.session.delete(msg)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as exception:
        current_app.logger.exception("Erro ao excluir mensagem (id=%s): %s", id_msg, str(exception))
        db.session.rollback()
        return jsonify({"error": "Erro interno ao excluir mensagem", "detail": str(exception)}), 500

@views.route("/api/solicitacoes", methods=["GET"])
@login_required
def api_solicitacoes():
    if getattr(current_user, "id_cargo_usuario", None) != 2:
        return jsonify([]), 403
    
    canal = (request.args.get("canal") or "").lower()

    if canal not in ("aluno", "tec", "prof", "coor", "dir"):
        return jsonify([])
    
    etec = getattr(current_user, "etec_tec", None)
    id_etec = getattr(etec, "id_etec", None)

    if id_etec is None:
        return jsonify([])

    filtro = []

    if canal == "aluno":
        filtro = [Solicitacoes.id_aluno_solict.isnot(None), Solicitacoes.id_etec_solict == id_etec]
    elif canal == "tec":
        filtro = [Solicitacoes.id_tec_solict.isnot(None), Solicitacoes.id_etec_solict == id_etec]
    elif canal == "prof":
        filtro = [Solicitacoes.id_prof_solict.isnot(None), Solicitacoes.id_etec_solict == id_etec]
    elif canal == "coor":
        filtro = [Solicitacoes.id_coor_solict.isnot(None), Solicitacoes.id_etec_solict == id_etec]
    elif canal == "dir":
        filtro = [Solicitacoes.id_dir_solict.isnot(None), Solicitacoes.id_etec_solict == id_etec]

    solicitacoes = Solicitacoes.query.filter(*filtro).order_by(Solicitacoes.data_hora_solict.asc()).all()

    resultado = []

    for solicitacao in solicitacoes:
        id_usuario = None
        nome_usuario = None
        usuario = None

        if solicitacao.aluno_solict:
            id_usuario = solicitacao.id_aluno_solict
            nome_usuario = solicitacao.aluno_solict.nome_aluno
            usuario = solicitacao.aluno_solict
        elif solicitacao.tec_solict:
            id_usuario = solicitacao.id_tec_solict
            nome_usuario = solicitacao.tec_solict.nome_tec
            usuario = solicitacao.tec_solict
        elif solicitacao.prof_solict:
            id_usuario = solicitacao.id_prof_solict
            nome_usuario = solicitacao.prof_solict.nome_prof
            usuario = solicitacao.prof_solict
        elif solicitacao.coor_solict:
            id_usuario = solicitacao.id_coor_solict
            nome_usuario = solicitacao.coor_solict.nome_coor
            usuario = solicitacao.coor_solict
        elif solicitacao.dir_solict:
            id_usuario = solicitacao.id_dir_solict
            nome_usuario = solicitacao.dir_solict.nome_dir
            usuario = solicitacao.dir_solict

        resultado.append({
            "id_solict": solicitacao.id_solict,
            "data_hora_solict": converter_fuso_horario(solicitacao.data_hora_solict),
            "tipo": canal,
            "id_usuario": id_usuario,
            "nome_usuario": nome_usuario,
            "rotulo_emissor": rotulo_emissor(canal, usuario)
        })
    
    return jsonify(resultado)

@views.route("/api/solicitacoes/redefinir", methods=["POST"])
@login_required
def api_solicitacoes_redefinir():
    if getattr(current_user, "id_cargo_usuario", None) != 2:
        return jsonify({"error": "Permissão negada"}), 403
    
    payload = request.get_json(silent=True) or request.form.to_dict() or {}
    id_solict_bruto = payload.get("id_solict")
    tipo_bruto = payload.get("tipo") or payload.get("tipo_usuario") or payload.get("tipoUsuario") or ""

    try:
        id_solict = int(id_solict_bruto)
    except Exception:
        id_solict = None

    tipo = (str(tipo_bruto).strip().lower() if tipo_bruto is not None else "")

    if not id_solict or not tipo:
        return jsonify({"error": "Dados incompletos"}), 400

    solicitacao = Solicitacoes.query.get(id_solict)

    if not solicitacao:
        return jsonify({"error": "Solicitação não encontrada"}), 404

    etec = getattr(current_user, "etec_tec", None)
    id_etec = getattr(etec, "id_etec", None)

    if id_etec is None or solicitacao.id_etec_solict != id_etec:
        return jsonify({"error": "Permissão negada"}), 403

    try:
        if tipo == "aluno" and solicitacao.aluno_solict:
            usuario = solicitacao.aluno_solict
            usuario.senha_aluno = generate_password_hash(usuario.cpf_aluno)
        elif tipo == "tec" and solicitacao.tec_solict:
            usuario = solicitacao.tec_solict
            usuario.senha_tec = generate_password_hash(usuario.cpf_tec)
        elif tipo == "prof" and solicitacao.prof_solict:
            usuario = solicitacao.prof_solict
            usuario.senha_prof = generate_password_hash(usuario.cpf_prof)
        elif tipo == "coor" and solicitacao.coor_solict:
            usuario = solicitacao.coor_solict
            usuario.senha_coor = generate_password_hash(usuario.cpf_coor)
        elif tipo == "dir" and solicitacao.dir_solict:
            usuario = solicitacao.dir_solict
            usuario.senha_dir = generate_password_hash(usuario.cpf_dir)
        else:
            return jsonify({"error": "Solicitação inválida para este tipo"}), 400

        db.session.delete(solicitacao)
        db.session.commit()

        return jsonify({"success": True})
    except Exception as exception:
        current_app.logger.exception("Erro ao redefinir senha (solicitação id=%s, tipo=%s): %s", id_solict, tipo, str(exception))
        db.session.rollback()
        return jsonify({"error": "Erro interno ao redefinir senha", "detail": str(exception)}), 500

@views.route("/api/solicitacoes/excluir", methods=["POST"])
@login_required
def api_solicitacoes_excluir():
    if getattr(current_user, "id_cargo_usuario", None) != 2:
        return jsonify({"error": "Permissão negada"}), 403

    payload = request.get_json(silent=True) or request.form.to_dict() or {}
    id_solict_bruto = payload.get("id_solict")
    tipo_bruto = payload.get("tipo") or payload.get("tipo_usuario") or payload.get("tipoUsuario") or ""

    try:
        id_solict = int(id_solict_bruto)
    except Exception:
        id_solict = None

    tipo = (str(tipo_bruto).strip().lower() if tipo_bruto is not None else "")

    if not id_solict or not tipo:
        return jsonify({"error": "Dados incompletos"}), 400

    solicitacao = Solicitacoes.query.get(id_solict)

    if not solicitacao:
        return jsonify({"error": "Solicitação não encontrada"}), 404

    etec = getattr(current_user, "etec_tec", None)
    id_etec = getattr(etec, "id_etec", None)

    if id_etec is None or solicitacao.id_etec_solict != id_etec:
        return jsonify({"error": "Permissão negada"}), 403

    try:
        db.session.delete(solicitacao)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as exception:
        current_app.logger.exception("Erro ao excluir solicitação (id=%s, tipo=%s): %s", id_solict, tipo, str(exception))
        db.session.rollback()
        return jsonify({"error": "Erro interno ao excluir solicitação", "detail": str(exception)}), 500

@views.route("/login", methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("views.index"))
    
    cidades = Cidades.query.order_by(Cidades.nome_cidade).all()
    etecs = Etecs.query.order_by(Etecs.nome_etec).all()
    cargos = Cargos.query.order_by(Cargos.id_cargo).all()

    if request.method == "POST":
        try:
            tipo_usuario = int(request.form.get("tipo_usuario", 0))
        except Exception:
            tipo_usuario = 0

        etec_usuario = str(request.form.get("etec_usuario", "")).strip()
        login_usuario = str(request.form.get("login_usuario", "")).strip()
        senha_usuario = request.form.get("senha_usuario", "") or ""

        if not etec_usuario or not login_usuario:
            flash("Preencha ETEC e usuário", "danger")
            return redirect(url_for("views.login"))

        etec = Etecs.query.filter_by(codigo_etec=etec_usuario).first()

        if not etec:
            flash("ETEC inexistente", "danger")
            return redirect(url_for("views.login"))

        def conferir_senha(usuario, senha_digitada, cpf_usuario=None, campo_senha=None):
            try:
                validacao_senha = getattr(usuario, "check_password", None)
                if validacao_senha:
                    primeiro_acesso = validacao_senha(cpf_usuario) if cpf_usuario else False
                    correspondencia = validacao_senha(senha_digitada)
                else:
                    hash = getattr(usuario, campo_senha)
                    primeiro_acesso = check_password_hash(hash, cpf_usuario) if cpf_usuario else False 
                    correspondencia = check_password_hash(hash, senha_digitada)

                return primeiro_acesso, correspondencia
            except Exception:
                return False, False
            
        if tipo_usuario == 1:
            aluno = Alunos.query.filter_by(rm_aluno=login_usuario).first()

            if not aluno:
                flash("Usuário ou senha incorretos", "danger")
                return redirect(url_for("views.login"))
            
            if etec.id_etec != aluno.id_etec_aluno:
                flash("ETEC inválida", "danger")
                return redirect(url_for("views.login"))
            
            primeiro_acesso, correspondencia = conferir_senha(aluno, senha_usuario, cpf_usuario=aluno.cpf_aluno, campo_senha="senha_aluno")

            if primeiro_acesso and senha_usuario == aluno.cpf_aluno:
                session["session_tipo_usuario"] = tipo_usuario
                session["session_login_usuario"] = login_usuario
                return redirect(url_for("views.primeiro_acesso"))
            
            if correspondencia:
                login_user(aluno)
                return redirect(url_for("views.index"))
            
            flash("Usuário ou senha incorretos", "danger")
        elif tipo_usuario == 2:
            tecnico = Tecnicos.query.filter_by(login_tec=login_usuario).first()

            if not tecnico:
                flash("Usuário ou senha incorretos", "danger")
                return redirect(url_for("views.login"))

            if etec.id_etec != tecnico.id_etec_tec:
                flash("ETEC inválida", "danger")
                return redirect(url_for("views.login"))

            primeiro_acesso, correspondencia = conferir_senha(tecnico, senha_usuario, cpf_usuario=tecnico.cpf_tec, campo_senha="senha_tec")

            if primeiro_acesso and senha_usuario == tecnico.cpf_tec:
                session["session_tipo_usuario"] = tipo_usuario
                session["session_login_usuario"] = login_usuario
                return redirect(url_for("views.primeiro_acesso"))
            
            if correspondencia:
                login_user(tecnico)
                return redirect(url_for("views.index"))
            
            flash("Usuário ou senha incorretos", "danger")
        elif tipo_usuario == 3:
            professor = Professores.query.filter_by(login_prof=login_usuario).first()

            if not professor:
                flash("Usuário ou senha incorretos", "danger")
                return redirect(url_for("views.login"))

            if etec.id_etec != professor.id_etec_prof:
                flash("ETEC inválida", "danger")
                return redirect(url_for("views.login"))

            primeiro_acesso, correspondencia = conferir_senha(professor, senha_usuario, cpf_usuario=professor.cpf_prof, campo_senha="senha_prof")
            
            if primeiro_acesso and senha_usuario == professor.cpf_prof:
                session["session_tipo_usuario"] = tipo_usuario
                session["session_login_usuario"] = login_usuario
                return redirect(url_for("views.primeiro_acesso"))
            
            if correspondencia:
                login_user(professor)
                return redirect(url_for("views.index"))
            
            flash("Usuário ou senha incorretos", "danger")
        elif tipo_usuario == 4:
            coordenador = Coordenadores.query.filter_by(login_coor=login_usuario).first()

            if not coordenador:
                flash("Usuário ou senha incorretos", "danger")
                return redirect(url_for("views.login"))

            if etec.id_etec != coordenador.id_etec_coor:
                flash("ETEC inválida", "danger")
                return redirect(url_for("views.login"))

            primeiro_acesso, correspondencia = conferir_senha(coordenador, senha_usuario, cpf_usuario=coordenador.cpf_coor, campo_senha="senha_coor")

            if primeiro_acesso and senha_usuario == coordenador.cpf_coor:
                session["session_tipo_usuario"] = tipo_usuario
                session["session_login_usuario"] = login_usuario
                return redirect(url_for("views.primeiro_acesso"))
            
            if correspondencia:
                login_user(coordenador)
                return redirect(url_for("views.index"))
            
            flash("Usuário ou senha incorretos", "danger")
        elif tipo_usuario == 5:
            diretor = Diretores.query.filter_by(login_dir=login_usuario).first()

            if not diretor:
                flash("Usuário ou senha incorretos", "danger")
                return redirect(url_for("views.login"))

            if etec.id_etec != diretor.id_etec_dir:
                flash("ETEC inválida", "danger")
                return redirect(url_for("views.login"))

            primeiro_acesso, correspondencia = conferir_senha(diretor, senha_usuario, cpf_usuario=diretor.cpf_dir, campo_senha="senha_dir")

            if primeiro_acesso and senha_usuario == diretor.cpf_dir:
                session["session_tipo_usuario"] = tipo_usuario
                session["session_login_usuario"] = login_usuario
                return redirect(url_for("views.primeiro_acesso"))
            
            if correspondencia:
                login_user(diretor)
                return redirect(url_for("views.index"))
            flash("Usuário ou senha incorretos", "danger")
        else:
            flash("Tipo de usuário inválido", "danger")

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

@views.route("/api/solicitacoes/solicitar", methods=["POST"])
def api_solicitar_redefinicao():
    payload = request.get_json(force=True, silent=True) or request.form or {}

    tipo_usuario = payload.get("tipo_usuario")
    etec_usuario = payload.get("etec_usuario")
    login_usuario = payload.get("login_usuario")
    cpf_usuario = payload.get("cpf_usuario") or payload.get("senha_usuario") or payload.get("senha") or ""

    try:
        tipo_usuario = int(tipo_usuario)
    except:
        return jsonify({"error": "Tipo de usuário inválido"}), 400
    
    if tipo_usuario not in (1, 2, 3, 4, 5):
        return jsonify({"error": "Tipo de usuário inválido"}), 400
    
    if not etec_usuario or not str(etec_usuario).strip():
        return jsonify({"error": "Código da ETEC ausente"}), 400
    
    if not login_usuario or not str(login_usuario).strip():
        return jsonify({"error": "Login/RM ausente"}), 400
    
    digitos_cpf = re.sub(r"\D", "", str(cpf_usuario or ""))

    if not digitos_cpf or len(digitos_cpf) != 11:
        return jsonify({"error": "CPF ausente ou inválido (11 dígitos)"}), 400

    etec = Etecs.query.filter_by(codigo_etec=str(etec_usuario).strip()).first()

    if not etec:
        return jsonify({"error": "ETEC inexistente"}), 400

    id_etec = etec.id_etec
    usuario = None
    tipo = None

    try:
        if tipo_usuario == 1:
            usuario = Alunos.query.filter_by(rm_aluno=str(login_usuario).strip()).first()
            
            if not usuario:
                return jsonify({"error": "Aluno não encontrado"}), 404
            
            if usuario.id_etec_aluno != id_etec:
                return jsonify({"error": "ETEC inválida para esse aluno"}), 400
            
            cpf = re.sub(r"\D", "", str(getattr(usuario, "cpf_aluno", "") or ""))

            if cpf != digitos_cpf:
                return jsonify({"error": "CPF inválido"}), 400
            
            tipo = "aluno"
        elif tipo_usuario == 2:
            usuario = Tecnicos.query.filter_by(login_tec=str(login_usuario).strip()).first()
            
            if not usuario:
                return jsonify({"error": "Aluno não encontrado"}), 404
            
            if usuario.id_etec_tec != id_etec:
                return jsonify({"error": "ETEC inválida para esse aluno"}), 400
            
            cpf = re.sub(r"\D", "", str(getattr(usuario, "cpf_tec", "") or ""))

            if cpf != digitos_cpf:
                return jsonify({"error": "CPF inválido"}), 400

            tipo = "tec"
        elif tipo_usuario == 3:
            usuario = Professores.query.filter_by(login_prof=str(login_usuario).strip()).first()
            
            if not usuario:
                return jsonify({"error": "Aluno não encontrado"}), 404
            
            if usuario.id_etec_prof != id_etec:
                return jsonify({"error": "ETEC inválida para esse aluno"}), 400
            
            cpf = re.sub(r"\D", "", str(getattr(usuario, "cpf_prof", "") or ""))

            if cpf != digitos_cpf:
                return jsonify({"error": "CPF inválido"}), 400

            tipo = "prof"
        elif tipo_usuario == 4:
            usuario = Coordenadores.query.filter_by(login_coor=str(login_usuario).strip()).first()
            
            if not usuario:
                return jsonify({"error": "Aluno não encontrado"}), 404
            
            if usuario.id_etec_coor != id_etec:
                return jsonify({"error": "ETEC inválida para esse aluno"}), 400

            cpf = re.sub(r"\D", "", str(getattr(usuario, "cpf_coor", "") or ""))
            if cpf != digitos_cpf:
                return jsonify({"error": "CPF inválido"}), 400

            tipo = "coor"
        elif tipo_usuario == 5:
            usuario = Diretores.query.filter_by(login_dir=str(login_usuario).strip()).first()
            
            if not usuario:
                return jsonify({"error": "Aluno não encontrado"}), 404
            
            if usuario.id_etec_dir != id_etec:
                return jsonify({"error": "ETEC inválida para esse aluno"}), 400

            cpf = re.sub(r"\D", "", str(getattr(usuario, "cpf_dir", "") or ""))

            if cpf != digitos_cpf:
                return jsonify({"error": "CPF inválido"}), 400
            
            tipo = "dir"
    except Exception:
        return jsonify({"error": "Erro ao buscar usuário"}), 500

    filtro = { "id_etec_solict": id_etec }

    if tipo == "aluno":
        filtro["id_aluno_solict"] = usuario.id_aluno
    elif tipo == "tec":
        filtro["id_tec_solict"] = usuario.id_tec
    elif tipo == "prof":
        filtro["id_prof_solict"] = usuario.id_prof
    elif tipo == "coor":
        filtro["id_coor_solict"] = usuario.id_coor
    elif tipo == "dir":
        filtro["id_dir_solict"] = usuario.id_dir

    ja_existe = Solicitacoes.query.filter_by(**filtro).first()

    if ja_existe:
        return jsonify({"error": "Já existe uma solicitação pendente para este usuário"}), 409

    try:
        nova = Solicitacoes(id_etec_solict=id_etec)
        if tipo == "aluno":
            nova.id_aluno_solict = usuario.id_aluno
        elif tipo == "tec":
            nova.id_tec_solict = usuario.id_tec
        elif tipo == "prof":
            nova.id_prof_solict = usuario.id_prof
        elif tipo == "coor":
            nova.id_coor_solict = usuario.id_coor
        elif tipo == "dir":
            nova.id_dir_solict = usuario.id_dir

        db.session.add(nova)
        db.session.commit()

        return jsonify({"success": True, "id_solict": nova.id_solict}), 201
    except Exception as exception:
        db.session.rollback()
        current_app.logger.exception("Erro ao criar solicitação: %s", exception)
        return jsonify({"error": "Erro ao criar solicitação"}), 500

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

@views.route("/perfil/alterar_senha", methods=["GET", "POST"])
@login_required
def alterar_senha():
    if request.method == "POST":
        senha_atual = (request.form.get("senha_atual") or "").strip()
        nova_senha = (request.form.get("nova_senha") or "").strip()
        confirmar_senha = (request.form.get("confirmar_senha") or "").strip()

        if not senha_atual or not nova_senha or not confirmar_senha:
            flash("Preencha todos os campos", "warning")
            return redirect(url_for("views.alterar_senha"))

        if nova_senha != confirmar_senha:
            flash("As senhas não coincidem", "warning")
            return redirect(url_for("views.alterar_senha"))
        
        padrao = re.compile(r"(?=.*[A-Za-z])(?=.*\d).{6,}")

        if not padrao.fullmatch(nova_senha):
            flash("A nova senha deve ter mínimo 6 caracteres e incluir letras e números", "warning")
            return redirect(url_for("views.alterar_senha"))

        cargo_usuario = getattr(current_user, "id_cargo_usuario", None)

        if cargo_usuario == 1:
            hash_senha_atual = getattr(current_user, "senha_aluno", None)
            campo_senha = "senha_aluno"
        elif cargo_usuario == 2:
            hash_senha_atual = getattr(current_user, "senha_tec", None)
            campo_senha = "senha_tec"
        elif cargo_usuario == 3:
            hash_senha_atual = getattr(current_user, "senha_prof", None)
            campo_senha = "senha_prof"
        elif cargo_usuario == 4:
            hash_senha_atual = getattr(current_user, "senha_coor", None)
            campo_senha = "senha_coor"
        elif cargo_usuario == 5:
            hash_senha_atual = getattr(current_user, "senha_dir", None)
            campo_senha = "senha_dir"
        else:
            flash("Erro no cargo de usuário", "danger")
            return redirect(url_for("views.perfil"))

        if not hash_senha_atual:
            current_app.logger.error("Campo de senha ausente para usuário %s", current_user)
            flash("Erro interno: dados de usuário inválidos", "danger")
            return redirect(url_for("views.perfil"))

        if not check_password_hash(hash_senha_atual, senha_atual):
            flash("Senha atual incorreta", "danger")
            return redirect(url_for("views.alterar_senha"))

        if check_password_hash(hash_senha_atual, nova_senha):
            flash("A nova senha não pode ser igual à senha anterior", "danger")
            return redirect(url_for("views.alterar_senha"))

        try:
            setattr(current_user, campo_senha, generate_password_hash(nova_senha))
            db.session.commit()
        except SQLAlchemyError as error:
            db.session.rollback()
            current_app.logger.exception("Erro ao alterar senha: %s", error)
            flash("Ocorreu um erro ao salvar a nova senha. Tente novamente", "danger")
            return redirect(url_for("views.alterar_senha"))
        
        flash("Senha alterada com sucesso", "success")
        return redirect(url_for("views.perfil"))

    return render_template("alterar_senha.html")

@views.route("/perfil/editar_perfil", methods=["GET", "POST"])
@login_required
def editar_perfil():
    if request.method == "POST":
        cor = request.form.get("cor_avatar", "").strip()

        if not re.match(r"^#[0-9A-Fa-f]{6}$", cor):
            flash("Cor inválida.", "danger")
            return redirect(url_for("views.editar_perfil"))

        try:
            current_user.cor_avatar = cor
            db.session.add(current_user)
            db.session.commit()
            flash("Cor do perfil atualizada com sucesso", "success")
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.exception("Erro ao atualizar cor do avatar")
            flash("Ocorreu um erro ao salvar a cor. Tente novamente", "danger")
        
        return redirect(url_for("views.perfil"))

    return render_template("editar_perfil.html")

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

    login_usuario = str(login_usuario).strip()
    
    if request.method == "POST":
        senha_usuario = (request.form.get("senha_usuario") or "").strip()
        confirmar_senha_usuario = (request.form.get("confirmar_senha_usuario") or "").strip()

        if senha_usuario != confirmar_senha_usuario:
            flash("As senhas não coincidem", "danger")
            return redirect(url_for("views.primeiro_acesso"))
        
        if len(senha_usuario) < 6 or not re.search(r"[A-Za-z]", senha_usuario) or not re.search(r"\d", senha_usuario):
            flash("Senha inválida: mínimo 6 caracteres, incluindo letras e números", "danger")
            return redirect(url_for("views.primeiro_acesso"))
        
        def erro():
            session.pop("session_tipo_usuario", None)
            session.pop("session_login_usuario", None)
            flash("Erro ao processar primeiro acesso", "danger")
            return redirect(url_for("views.login"))

        try:
            if tipo_usuario == 1:
                usuario = Alunos.query.filter_by(rm_aluno=login_usuario).first()
                cpf_usuario = usuario.cpf_aluno if usuario else None
                validacao_senha = getattr(usuario, "check_password", None)
                cpf_valido = validacao_senha(cpf_usuario) if usuario and cpf_usuario and validacao_senha else False

                if not usuario:
                    return erro()

                if not cpf_valido:
                    session.pop("session_tipo_usuario", None)
                    session.pop("session_login_usuario", None)
                    flash("Primeiro acesso inválido ou já realizado", "danger")
                    return redirect(url_for("views.login"))

                usuario.senha_aluno = generate_password_hash(senha_usuario)
            elif tipo_usuario == 2:
                usuario = Tecnicos.query.filter_by(login_tec=login_usuario).first()
                cpf_usuario = usuario.cpf_tec if usuario else None
                validacao_senha = getattr(usuario, "check_password", None)
                cpf_valido = validacao_senha(cpf_usuario) if usuario and cpf_usuario and validacao_senha else False

                if not usuario:
                    return erro()

                if not cpf_valido:
                    session.pop("session_tipo_usuario", None)
                    session.pop("session_login_usuario", None)
                    flash("Primeiro acesso inválido ou já realizado", "danger")
                    return redirect(url_for("views.login"))
                
                usuario.senha_tec = generate_password_hash(senha_usuario)
            elif tipo_usuario == 3:
                usuario = Professores.query.filter_by(login_prof=login_usuario).first()
                cpf_usuario = usuario.cpf_prof if usuario else None
                validacao_senha = getattr(usuario, "check_password", None)
                cpf_valido = validacao_senha(cpf_usuario) if usuario and cpf_usuario and validacao_senha else False

                if not usuario:
                    return erro()

                if not cpf_valido:
                    session.pop("session_tipo_usuario", None)
                    session.pop("session_login_usuario", None)
                    flash("Primeiro acesso inválido ou já realizado", "danger")
                    return redirect(url_for("views.login"))

                usuario.senha_prof = generate_password_hash(senha_usuario)
            elif tipo_usuario == 4:
                usuario = Coordenadores.query.filter_by(login_coor=login_usuario).first()
                cpf_usuario = usuario.cpf_coor if usuario else None
                validacao_senha = getattr(usuario, "check_password", None)
                cpf_valido = validacao_senha(cpf_usuario) if usuario and cpf_usuario and validacao_senha else False

                if not usuario:
                    return erro()

                if not cpf_valido:
                    session.pop("session_tipo_usuario", None)
                    session.pop("session_login_usuario", None)
                    flash("Primeiro acesso inválido ou já realizado", "danger")
                    return redirect(url_for("views.login"))
                
                usuario.senha_coor = generate_password_hash(senha_usuario)
            elif tipo_usuario == 5:
                usuario = Diretores.query.filter_by(login_dir=login_usuario).first()
                cpf_usuario = usuario.cpf_dir if usuario else None
                validacao_senha = getattr(usuario, "check_password", None)
                cpf_valido = validacao_senha(cpf_usuario) if usuario and cpf_usuario and validacao_senha else False

                if not usuario:
                    return erro()

                if not cpf_valido:
                    session.pop("session_tipo_usuario", None)
                    session.pop("session_login_usuario", None)
                    flash("Primeiro acesso inválido ou já realizado", "danger")
                    return redirect(url_for("views.login"))

                usuario.senha_dir = generate_password_hash(senha_usuario)
            else:
                flash("Tipo de usuário inválido", "danger")
                return redirect(url_for("views.login"))
            
            try:
                db.session.commit()
            except SQLAlchemyError as error:
                db.session.rollback()
                current_app.logger.exception("Erro ao gravar nova senha no primeiro acesso: %s", error)
                return erro()

            session.pop("session_tipo_usuario", None)
            session.pop("session_login_usuario", None)

            try:
                login_user(usuario)
            except Exception:
                flash("Senha redefinida com sucesso! Faça login", "success")
                return redirect(url_for("views.login"))
            
            flash("Senha redefinida com sucesso!", "success")
            return redirect(url_for("views.index"))
        except Exception as exception:
            current_app.logger.exception("Erro inesperado em primeiro_acesso: %s", exception)
            return erro()

    return render_template("primeiro_acesso.html", login_usuario=login_usuario)