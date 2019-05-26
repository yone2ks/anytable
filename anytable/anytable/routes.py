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

@anytable_bp.route('/<id>')
def show(id):
    anytable = AnyTable.query.get(id)
    return render_template('anytable/show.html', anytable=anytable)

@anytable_bp.route('/new')
def new():
    form = AnyTableForm()
    return render_template('anytable/new.html', form=form)

@anytable_bp.route('/create', methods=['POST'])
def create():
    table_name = request.form['table_name']
    description = request.form['description']
    fields = []
    print(request.form)
    for var_org in range(int(request.form['field_num'])):
        var = var_org + 1
        fields.append({"name": request.form['field'+str(var)+'_name'], "type": request.form['field'+str(var)+'_type'], "unique": "true" if request.form.get('field'+str(var)+'_unique')=="1" else "false", "nullable": "true" if request.form.get('field'+str(var)+'_nullable')=="1" else "false"})
    table_schema = {"table_name": table_name, "description": description, "fields": fields}
    anytable = AnyTable(table_name=table_name, description=description, table_schema = json.dumps(table_schema))
    db.session.add(anytable)
    db.session.commit()
    return redirect(url_for('anytable.index'))


