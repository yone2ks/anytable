import json, datetime
from distutils.util import strtobool
from flask import jsonify, request, current_app, redirect, url_for, render_template, flash, session
from flask_restplus import Resource, Namespace
from dynaconf import settings
from inflector import Inflector
from anytable.extensions import ma, api, db
from anytable.blueprints import bp_factory
from .models import AnyTable
from .forms import AnyTableForm

anytable_bp = bp_factory('anytable')

@anytable_bp.route('')
def index():
    anytables = AnyTable.query.all()
    return render_template('anytable/index.html', anytables=anytables)

@anytable_bp.route('/<int:id>')
def show(id):
    anytable = AnyTable.query.get(id)
    anytables = AnyTable.query.all()
    return render_template('anytable/show.html', anytable=anytable, anytables=anytables)

@anytable_bp.route('/new')
def new():
    form = AnyTableForm()
    anytables = AnyTable.query.all()
    return render_template('anytable/new.html', form=form, anytables=anytables)

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

@anytable_bp.route('/<string:cls>')
def cls_index(cls):
    cls_index = list(map(lambda item: item.__dict__, AnyTable.models[cls].query.all()))
    fields = list(map(lambda field: field["name"], AnyTable.table_schemas[cls]["fields"]))
    anytables = AnyTable.query.all()
    return render_template('anytable/common_index.html', cls_index=cls_index, fields=fields, cls=cls, anytables=anytables)

@anytable_bp.route('/<string:cls>/new')
def cls_new(cls):
    form = AnyTable.forms[cls]()
    fields = list(map(lambda field: field["name"], AnyTable.table_schemas[cls]["fields"]))
    anytables = AnyTable.query.all()
    return render_template('anytable/common_new.html', form=form, fields=fields, cls=cls, anytables=anytables)

@anytable_bp.route('/<string:cls>/create', methods=['POST'])
def cls_create(cls):
    fields = list(map(lambda field: field["name"], AnyTable.table_schemas[cls]["fields"]))
    types = list(map(lambda field: field["type"], AnyTable.table_schemas[cls]["fields"]))
    params = {}
    for index, field in enumerate(fields):
        print(types[index])
        if types[index] == 'date':
            params[field] = datetime.datetime.strptime(request.form[field], "%Y-%m-%d")
        elif types[index] == 'boolean':
            params[field] = strtobool(request.form[field])
        else:
            params[field] = request.form[field]
    record = AnyTable.models[cls](**params)
    db.session.add(record)
    db.session.commit()
    return redirect(url_for('anytable.cls_index', cls=cls))

@anytable_bp.route('/<string:cls>/<int:id>')
def cls_show(cls, id):
    record = AnyTable.models[cls].query.get(id)
    fields = list(map(lambda field: field["name"], AnyTable.table_schemas[cls]["fields"]))
    anytables = AnyTable.query.all()
    return render_template('anytable/common_show.html', record=record, fields=fields, cls=cls, anytables=anytables)

@anytable_bp.route('/<string:cls>/<int:id>/edit')
def cls_edit(cls, id):
    form = AnyTable.forms[cls]()
    fields = list(map(lambda field: field["name"], AnyTable.table_schemas[cls]["fields"]))
    anytables = AnyTable.query.all()
    record = AnyTable.models[cls].query.get(id)
    return render_template('anytable/common_edit.html', form=form, fields=fields, cls=cls, anytables=anytables, record=record, id=id)


@anytable_bp.route('/<string:cls>/<int:id>/update', methods=['POST'])
def cls_update(cls, id):
    record = AnyTable.models[cls].query.get(id)
    fields = list(map(lambda field: field["name"], AnyTable.table_schemas[cls]["fields"]))
    for field in fields:
        setattr(record, field, request.form[field])
    record.update()
    return redirect(url_for('anytable.cls_index', cls=cls))

@anytable_bp.route('/<string:cls>/<int:id>/delete')
def cls_delete(cls, id):
    record = AnyTable.models[cls].query.get(id)
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for('anytable.cls_index', cls=cls))


