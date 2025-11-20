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

    from .views import views
    app.register_blueprint(views)

    @app.errorhandler(404)
    def not_found(e):
        return "Página não encontrada", 404

    return app