from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash

class Cidades(db.Model):
    __tablename__ = "cidades"
    id_cidade = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_cidade = db.Column(db.String(128), nullable=False)

class Etecs(db.Model):
    __tablename__ = "etecs"
    id_etec = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codigo_etec = db.Column(db.String(3), unique=True, nullable=False)
    nome_etec = db.Column(db.String(128), nullable=False)
    id_cidade_etec = db.Column(db.Integer, db.ForeignKey("cidades.id_cidade"), nullable=False)

class Cursos(db.Model):
    __tablename__ = "cursos"
    id_curso = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricao_curso = db.Column(db.String(128), nullable=False)
    turno_curso = db.Column(db.String(128), nullable=False)
    qtd_modulos_curso = db.Column(db.Integer, nullable=False)

class Materias(db.Model):
    __tablename__ = "materias"
    id_materia = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricao_materia = db.Column(db.String(128), nullable=False)

class Cargos(db.Model):
    __tablename__ = "cargos"
    id_cargo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricao_cargo = db.Column(db.String(128), nullable=False)

class Alunos(db.Model, UserMixin):
    __tablename__ = "alunos"
    id_aluno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rm_aluno = db.Column(db.String(6), nullable=False)
    senha_aluno = db.Column(db.String(128), nullable=False)
    cpf_aluno = db.Column(db.String(11), nullable=False)
    nome_aluno = db.Column(db.String(128), nullable=False)
    modulo_aluno = db.Column(db.Integer, nullable=False)
    turma_aluno = db.Column(db.String(1), nullable=False)
    situacao_aluno = db.Column(db.String(128), nullable=False)
    ano_origem_aluno = db.Column(db.Integer, nullable=False)
    id_curso_aluno = db.Column(db.Integer, db.ForeignKey("cursos.id_curso"), nullable=False)
    id_etec_aluno = db.Column(db.Integer, db.ForeignKey("etecs.id_etec"), nullable=False)

    def __init__(self, rm_aluno, cpf_aluno, nome_aluno, modulo_aluno, turma_aluno, situacao_aluno, ano_origem_aluno, id_curso_aluno, id_etec_aluno, senha_texto=None):
        self.rm_aluno = rm_aluno
        self.cpf_aluno = cpf_aluno
        self.nome_aluno = nome_aluno
        self.modulo_aluno = modulo_aluno
        self.turma_aluno = turma_aluno
        self.situacao_aluno = situacao_aluno
        self.ano_origem_aluno = ano_origem_aluno
        self.id_curso_aluno = id_curso_aluno
        self.id_etec_aluno = id_etec_aluno

        if senha_texto:
            self.senha_aluno = generate_password_hash(senha_texto)
        else:
            self.senha_aluno = generate_password_hash(cpf_aluno)

    @property
    def id(self):
        return self.id_aluno
    
class Professores(db.Model, UserMixin):
    __tablename__ = "professores"
    id_prof = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login_prof = db.Column(db.String(11), nullable=False)
    senha_prof = db.Column(db.String(128), nullable=False)
    cpf_prof = db.Column(db.String(11), nullable=False)
    nome_prof = db.Column(db.String(128), nullable=False)
    id_etec_prof = db.Column(db.Integer, db.ForeignKey("etecs.id_etec"), nullable=False)

    def __init__(self, login_prof, cpf_prof, nome_prof, id_etec_prof, senha_texto=None):
        self.login_prof = login_prof
        self.cpf_prof = cpf_prof
        self.nome_prof = nome_prof
        self.id_etec_prof = id_etec_prof
        if senha_texto:
            self.senha_prof = generate_password_hash(senha_texto)
        else:
            self.senha_prof = generate_password_hash(cpf_prof)

    @property
    def id(self):
        return self.id_prof

class Administradores(db.Model, UserMixin):
    __tablename__ = "administradores"
    id_adm = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login_adm = db.Column(db.String(11), nullable=False)
    senha_adm = db.Column(db.String(128), nullable=False)
    cpf_adm = db.Column(db.String(11), nullable=False)
    nome_adm = db.Column(db.String(128), nullable=False)
    id_etec_adm = db.Column(db.Integer, db.ForeignKey("etecs.id_etec"), nullable=False)

    def __init__(self, login_adm, cpf_adm, nome_adm, id_etec_adm, senha_texto=None):
        self.login_adm = login_adm
        self.cpf_adm = cpf_adm
        self.nome_adm = nome_adm
        self.id_etec_adm = id_etec_adm
        if senha_texto:
            self.senha_adm = generate_password_hash(senha_texto)
        else:
            self.senha_adm = generate_password_hash(cpf_adm)

    @property
    def id(self):
        return self.id_adm

class Aulas(db.Model):
    __tablename__ = "aulas"
    id_aula = db.Column(db.Integer, primary_key=True, autoincrement=True)
    modulo_aula = db.Column(db.Integer, nullable=False)
    turma_aula = db.Column(db.String(2), nullable=False)
    id_curso_aula = db.Column(db.Integer, db.ForeignKey("cursos.id_curso"), nullable=False)
    id_materia_aula = db.Column(db.Integer, db.ForeignKey("materias.id_materia"), nullable=False)
    id_professor_aula = db.Column(db.Integer, db.ForeignKey("professores.id_prof"), nullable=False)
    id_etec_aula = db.Column(db.Integer, db.ForeignKey("etecs.id_etec"), nullable=False)

class Canais(db.Model):
    __tablename__ = "canais"
    id_canal = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricao_canal = db.Column(db.String(128), nullable=False)
    id_cargo_editor_canal = db.Column(db.Integer, db.ForeignKey("cargos.id_cargo"), nullable=False)
    id_cargo_leitor_canal = db.Column(db.Integer, db.ForeignKey("cargos.id_cargo"), nullable=False)