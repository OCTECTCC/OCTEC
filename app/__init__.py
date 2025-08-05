from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_object="app.config.Config"):
    app = Flask(__name__)

    app.config.from_object(config_object)

    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "views.login"

    from .views import views
    app.register_blueprint(views)

    return app