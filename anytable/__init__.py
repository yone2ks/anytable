import os
import locale
import sqlite3
import json
from flask import Flask
from sqlalchemy import exc
from flask_security import Security, login_required, SQLAlchemySessionUserDatastore
from dynaconf import FlaskDynaconf
import anytable as app_root
from .extensions import db, bootstrap, security, api, ma
from .user.models import User, Role
from .base.routes import base_bp
from .apis.routes import api_bp, anytable_ns
from .anytable.routes import anytable_bp
from .anytable.models import AnyTable


APP_ROOT_FOLDER = os.path.abspath(os.path.dirname(app_root.__file__))
TEMPLATE_FOLDER = os.path.join(APP_ROOT_FOLDER, 'templates')
STATIC_FOLDER = os.path.join(APP_ROOT_FOLDER, 'static')

app = Flask(__name__, template_folder=TEMPLATE_FOLDER, static_folder=STATIC_FOLDER)
FlaskDynaconf(app)
db.init_app(app)
bootstrap.init_app(app)
security.init_app(app, SQLAlchemySessionUserDatastore(db.session, User, Role))
api.init_app(app)
ma.init_app(app)

app.register_blueprint(base_bp)
app.register_blueprint(api_bp)
app.register_blueprint(anytable_bp)

api.add_namespace(anytable_ns)

@app.before_first_request
def create_db():
    db.create_all()

try:
    with app.app_context():
        for anytable in AnyTable.query.all():
            anytable.add_table()
except (exc.OperationalError, exc.ArgumentError) as e:
    print(e)

