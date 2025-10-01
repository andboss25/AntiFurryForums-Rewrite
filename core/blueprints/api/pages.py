
from flask import Blueprint

from core.utils import log
from core.utils import config
import os

config_loader = config.ConfigSet()
pages_blueprint = Blueprint("pages",__name__)

def render_html(name:str):
    data_file = open(os.path.join(
        "core",
        "blueprints",
        "pages",
        name + ".html"
    ),"r")

    data = data_file.read()
    data_file.close()

    return data

@pages_blueprint.route("/login")
def login_page():
    return render_html("login")

@pages_blueprint.route("/signup")
def signup_page():
    return render_html("signup")