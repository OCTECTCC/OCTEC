from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
loginManager = LoginManager()

def create_app(configObject="OCTEC.config.Config"):
    app = Flask(__name__)

    app.config.from_object(configObject)

    db.init_app(app)

    loginManager.init_app(app)
    loginManager.login_view = "views.login"

    from .views import views
    app.register_blueprint(views)

    return app