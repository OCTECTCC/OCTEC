from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_object="app.config.Config"):
    app = Flask(__name__)

    app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = "views.login"
    login_manager.login_message = "Por favor, entre para acessar esta página"
    login_manager.login_message_category = "info"

    from .models import Alunos, Tecnicos, Professores, Coordenadores, Diretores

    @login_manager.user_loader
    def load_user(id_usuario):
        if not id_usuario:
            return None
        
        tipo_usuario, separador, id_usuario_str = id_usuario.partition("-")

        if not separador:
            return None
        
        try:
            primary_key = int(id_usuario_str)
        except ValueError:
            return None

        if tipo_usuario == "aluno":
            return Alunos.query.get(primary_key)
        elif tipo_usuario == "tec":
            return Tecnicos.query.get(primary_key)
        elif tipo_usuario == "prof":
            return Professores.query.get(primary_key)
        elif tipo_usuario == "coor":
            return Coordenadores.query.get(primary_key)
        elif tipo_usuario == "dir":
            return Diretores.query.get(primary_key)
        return None

    from .views import views
    app.register_blueprint(views)

    @app.errorhandler(404)
    def not_found(e):
        return "Página não encontrada", 404

    return app