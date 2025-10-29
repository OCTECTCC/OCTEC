from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash

class Cidades(db.Model):
    __tablename__ = "cidades"
    id_cidade = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_cidade = db.Column(db.String(128), nullable=False)

    etecs_cidade = db.relationship("Etecs", back_populates="cidade_etec")

class Etecs(db.Model):
    __tablename__ = "etecs"
    id_etec = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codigo_etec = db.Column(db.String(3), unique=True, nullable=False)
    nome_etec = db.Column(db.String(128), nullable=False)

    id_cidade_etec = db.Column(db.Integer, db.ForeignKey("cidades.id_cidade"), nullable=False)
    cidade_etec = db.relationship("Cidades", back_populates="etecs_cidade")
    
    alunos_etec = db.relationship("Alunos", back_populates="etec_aluno")
    professores_etec = db.relationship("Professores", back_populates="etec_prof")
    coordenadores_etec = db.relationship("Coordenadores", back_populates="etec_coor")
    diretor_etec = db.relationship("Diretores", back_populates="etec_dir")
    aulas_etec = db.relationship("Aulas", back_populates="etec_aula")

coordenadores_cursos = db.Table(
    "coordenadores_cursos",
    db.Column("id_coor", db.Integer, db.ForeignKey("coordenadores.id_coor"), primary_key=True),
    db.Column("id_curso", db.Integer, db.ForeignKey("cursos.id_curso"), primary_key=True)
)

class Cursos(db.Model):
    __tablename__ = "cursos"
    id_curso = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sigla_curso = db.Column(db.String(10), nullable=False)
    descricao_curso = db.Column(db.String(128), nullable=False)
    turno_curso = db.Column(db.String(128), nullable=False)
    qtd_modulos_curso = db.Column(db.Integer, nullable=False)
    ensino_medio_integrado_curso = db.Column(db.Boolean, nullable=False)

    alunos_curso = db.relationship("Alunos", back_populates="curso_aluno")
    aulas_curso = db.relationship("Aulas", back_populates="curso_aula")

    coordenadores_curso = db.relationship("Coordenadores", secondary=coordenadores_cursos, back_populates="cursos_coor")

class Materias(db.Model):
    __tablename__ = "materias"
    id_materia = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricao_materia = db.Column(db.String(128), nullable=False)

    aulas_materia = db.relationship("Aulas", back_populates="materia_aula")

class Cargos(db.Model):
    __tablename__ = "cargos"
    id_cargo = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricao_cargo = db.Column(db.String(128), nullable=False)

    alunos_cargo = db.relationship("Alunos", back_populates="cargo_usuario")
    professores_cargo = db.relationship("Professores", back_populates="cargo_usuario")
    coordenadores_cargo = db.relationship("Coordenadores", back_populates="cargo_usuario")
    diretores_cargo = db.relationship("Diretores", back_populates="cargo_usuario")

    leitores_canais_cargo = db.relationship("Canais", back_populates="cargo_leitor_canal", foreign_keys="[Canais.id_cargo_leitor_canal]")
    emissores_canais_cargo = db.relationship("Canais", back_populates="cargo_emissor_canal", foreign_keys="[Canais.id_cargo_emissor_canal]")
    moderadores_canais_cargo = db.relationship("Canais", back_populates="cargo_moderador_canal", foreign_keys="[Canais.id_cargo_moderador_canal]")

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
    semestre_origem_aluno = db.Column(db.Integer, nullable=False)
    representante_aluno = db.Column(db.Boolean, nullable=False)

    id_curso_aluno = db.Column(db.Integer, db.ForeignKey("cursos.id_curso"), nullable=False)
    curso_aluno = db.relationship("Cursos", back_populates="alunos_curso")

    id_etec_aluno = db.Column(db.Integer, db.ForeignKey("etecs.id_etec"), nullable=False)
    etec_aluno = db.relationship("Etecs", back_populates="alunos_etec")

    id_cargo_usuario = db.Column(db.Integer, db.ForeignKey("cargos.id_cargo"), nullable=False)
    cargo_usuario = db.relationship("Cargos", back_populates="alunos_cargo")

    def __init__(self, rm_aluno, cpf_aluno, nome_aluno, modulo_aluno, turma_aluno, situacao_aluno, ano_origem_aluno, semestre_origem_aluno, representante_aluno, id_cargo_usuario, id_curso_aluno, id_etec_aluno, senha_texto=None):
        self.rm_aluno = rm_aluno
        self.cpf_aluno = cpf_aluno
        self.nome_aluno = nome_aluno
        self.modulo_aluno = modulo_aluno
        self.turma_aluno = turma_aluno
        self.situacao_aluno = situacao_aluno
        self.ano_origem_aluno = ano_origem_aluno
        self.semestre_origem_aluno = semestre_origem_aluno
        self.representante_aluno = representante_aluno
        self.id_cargo_usuario = id_cargo_usuario
        self.id_curso_aluno = id_curso_aluno
        self.id_etec_aluno = id_etec_aluno

        if senha_texto:
            self.senha_aluno = generate_password_hash(senha_texto)
        else:
            self.senha_aluno = generate_password_hash(cpf_aluno)

    @property
    def id(self):
        return self.id_aluno
    def get_id(self):
        return f"aluno-{self.id_aluno}"
    
class Professores(db.Model, UserMixin):
    __tablename__ = "professores"
    id_prof = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login_prof = db.Column(db.String(11), nullable=False)
    senha_prof = db.Column(db.String(128), nullable=False)
    cpf_prof = db.Column(db.String(11), nullable=False)
    nome_prof = db.Column(db.String(128), nullable=False)
    biblioteca_prof = db.Column(db.Boolean, nullable=False)

    id_etec_prof = db.Column(db.Integer, db.ForeignKey("etecs.id_etec"), nullable=False)
    etec_prof = db.relationship("Etecs", back_populates="professores_etec")

    id_cargo_usuario = db.Column(db.Integer, db.ForeignKey("cargos.id_cargo"), nullable=False)
    cargo_usuario = db.relationship("Cargos", back_populates="professores_cargo")

    aulas_prof = db.relationship("Aulas", back_populates="professor_aula")

    def __init__(self, login_prof, cpf_prof, nome_prof, biblioteca_prof, id_cargo_usuario, id_etec_prof, senha_texto=None):
        self.login_prof = login_prof
        self.cpf_prof = cpf_prof
        self.nome_prof = nome_prof
        self.biblioteca_prof = biblioteca_prof
        self.id_cargo_usuario = id_cargo_usuario
        self.id_etec_prof = id_etec_prof
        if senha_texto:
            self.senha_prof = generate_password_hash(senha_texto)
        else:
            self.senha_prof = generate_password_hash(cpf_prof)

    @property
    def id(self):
        return self.id_prof
    def get_id(self):
        return f"prof-{self.id_prof}"

class Coordenadores(db.Model, UserMixin):
    __tablename__ = "coordenadores"
    id_coor = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login_coor = db.Column(db.String(11), nullable=False)
    senha_coor = db.Column(db.String(128), nullable=False)
    cpf_coor = db.Column(db.String(11), nullable=False)
    nome_coor = db.Column(db.String(128), nullable=False)
    ensino_medio_coor = db.Column(db.Boolean, nullable=False)
    pedagogico_coor = db.Column(db.Boolean, nullable=False)

    id_etec_coor = db.Column(db.Integer, db.ForeignKey("etecs.id_etec"), nullable=False)
    etec_coor = db.relationship("Etecs", back_populates="coordenadores_etec")

    id_cargo_usuario = db.Column(db.Integer, db.ForeignKey("cargos.id_cargo"), nullable=False)
    cargo_usuario = db.relationship("Cargos", back_populates="coordenadores_cargo")

    cursos_coor = db.relationship("Cursos", secondary=coordenadores_cursos, back_populates="coordenadores_curso")

    def __init__(self, login_coor, cpf_coor, nome_coor, ensino_medio_coor, pedagogico_coor, id_cargo_usuario, id_etec_coor, senha_texto=None):
        self.login_coor = login_coor
        self.cpf_coor = cpf_coor
        self.nome_coor = nome_coor
        self.ensino_medio_coor = ensino_medio_coor
        self.pedagogico_coor = pedagogico_coor
        self.id_cargo_usuario = id_cargo_usuario
        self.id_etec_coor = id_etec_coor
        if senha_texto:
            self.senha_coor = generate_password_hash(senha_texto)
        else:
            self.senha_coor = generate_password_hash(cpf_coor)

    @property
    def id(self):
        return self.id_coor
    def get_id(self):
        return f"coor-{self.id_coor}"

class Diretores(db.Model, UserMixin):
    __tablename__ = "diretores"
    id_dir = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login_dir = db.Column(db.String(11), nullable=False)
    senha_dir = db.Column(db.String(128), nullable=False)
    cpf_dir = db.Column(db.String(11), nullable=False)
    nome_dir = db.Column(db.String(128), nullable=False)

    id_etec_dir = db.Column(db.Integer, db.ForeignKey("etecs.id_etec"), nullable=False)
    etec_dir = db.relationship("Etecs", back_populates="diretor_etec")

    id_cargo_usuario = db.Column(db.Integer, db.ForeignKey("cargos.id_cargo"), nullable=False)
    cargo_usuario = db.relationship("Cargos", back_populates="diretores_cargo")

    def __init__(self, login_dir, cpf_dir, nome_dir, id_cargo_usuario, id_etec_dir, senha_texto=None):
        self.login_dir = login_dir
        self.cpf_dir = cpf_dir
        self.nome_dir = nome_dir
        self.id_cargo_usuario = id_cargo_usuario
        self.id_etec_dir = id_etec_dir
        if senha_texto:
            self.senha_dir = generate_password_hash(senha_texto)
        else:
            self.senha_dir = generate_password_hash(cpf_dir)

    @property
    def id(self):
        return self.id_dir
    def get_id(self):
        return f"dir-{self.id_dir}"

class Aulas(db.Model):
    __tablename__ = "aulas"
    id_aula = db.Column(db.Integer, primary_key=True, autoincrement=True)
    modulo_aula = db.Column(db.Integer, nullable=False)
    turma_aula = db.Column(db.String(2), nullable=False)
    ano_aula = db.Column(db.Integer, nullable=False)
    semestre_aula = db.Column(db.Integer, nullable=False)

    id_curso_aula = db.Column(db.Integer, db.ForeignKey("cursos.id_curso"), nullable=False)
    curso_aula = db.relationship("Cursos", back_populates="aulas_curso")

    id_materia_aula = db.Column(db.Integer, db.ForeignKey("materias.id_materia"), nullable=False)
    materia_aula = db.relationship("Materias", back_populates="aulas_materia")

    id_professor_aula = db.Column(db.Integer, db.ForeignKey("professores.id_prof"), nullable=False)
    professor_aula = db.relationship("Professores", back_populates="aulas_prof")

    id_etec_aula = db.Column(db.Integer, db.ForeignKey("etecs.id_etec"), nullable=False)
    etec_aula = db.relationship("Etecs", back_populates="aulas_etec")

class Canais(db.Model):
    __tablename__ = "canais"
    id_canal = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricao_canal = db.Column(db.String(128), nullable=False)

    id_cargo_leitor_canal = db.Column(db.Integer, db.ForeignKey("cargos.id_cargo"), nullable=False)
    cargo_leitor_canal = db.relationship("Cargos", back_populates="leitores_canais_cargo", foreign_keys=[id_cargo_leitor_canal])

    id_cargo_emissor_canal = db.Column(db.Integer, db.ForeignKey("cargos.id_cargo"), nullable=False)
    cargo_emissor_canal = db.relationship("Cargos", back_populates="emissores_canais_cargo", foreign_keys=[id_cargo_emissor_canal])

    id_cargo_moderador_canal = db.Column(db.Integer, db.ForeignKey("cargos.id_cargo"), nullable=False)
    cargo_moderador_canal = db.relationship("Cargos", back_populates="moderadores_canais_cargo", foreign_keys=[id_cargo_moderador_canal])