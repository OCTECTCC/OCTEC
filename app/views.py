from flask import render_template, Blueprint
from . import login_manager

views = Blueprint("views", __name__)

@login_manager.user_loader
def load_user(user_id):
    return None

@views.route("/")
def index():
    return render_template("index.html")

@views.route("/login")
def login():
    return render_template("login.html")

@views.route("/primeiro_acesso")
def primeiro_acesso():
    return render_template("primeiro_acesso.html")