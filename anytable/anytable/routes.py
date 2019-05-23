import json
from flask import jsonify, request, current_app, redirect, url_for, render_template, flash, session
from flask_restplus import Resource, Namespace
from dynaconf import settings
from anytable.extensions import ma, api, db
from anytable.blueprints import bp_factory
from .models import AnyTable
from .forms import AnyTableForm

anytable_bp = bp_factory('anytable')

@anytable_bp.route('')
def index():
    page = request.args.get('page', 1, type=int)
    anytables = AnyTable.query.paginate(page, settings.PER_PAGE)
    return render_template('anytable/index.html', anytables=anytables)

@anytable_bp.route('/new')
def new():
    form = AnyTableForm()
    return render_template('anytable/new.html', form=form)

@anytable_bp.route('/create', methods=['POST'])
def create():
    return 
