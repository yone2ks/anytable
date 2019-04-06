import os
import locale
import sqlite3
from flask import Flask
from flask_security import Security, login_required, SQLAlchemySessionUserDatastore
from dynaconf import FlaskDynaconf
import app as app_root
from app.extensions import db, bootstrap, security, api, ma
from app.user.models import User, Role
from app.base.routes import base_bp

APP_ROOT_FOLDER = os.path.abspath(os.path.dirname(app_root.__file__))
TEMPLATE_FOLDER = os.path.join(APP_ROOT_FOLDER, 'templates')
STATIC_FOLDER = os.path.join(APP_ROOT_FOLDER, 'static')

app = Flask(__name__, template_folder=TEMPLATE_FOLDER, static_folder=STATIC_FOLDER)
FlaskDynaconf(app)
db.init_app(app)
bootstrap.init_app(app)
security.init_app(app, SQLAlchemySessionUserDatastore(db.session, User, Role))
ma.init_app(app)

app.register_blueprint(base_bp)

# Create a user to test with
@app.before_first_request
def create_db():
    db.create_all()

