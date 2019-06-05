import json
from flask import jsonify, request, current_app, redirect, url_for, render_template, flash, session
from flask_restplus import Resource, Namespace
from anytable.anytable.models import AnyTable
from anytable.extensions import ma, api, db
from anytable.blueprints import bp_factory

api_bp = bp_factory('api')

class AnyTableSchema(ma.ModelSchema):
    class Meta:
        model = AnyTable

anytables_schema = AnyTableSchema(many=True)
anytable_schema = AnyTableSchema()

anytable_ns = Namespace('anytables')

@api_bp.route('')
@anytable_ns.route('/')
class AnyTablesResource(Resource):
    def get(self):
        anytables = AnyTable.query.all()
        return anytables_schema.jsonify(anytables)

    def post(self):
        table_schema = request.get_json()
        table_name = table_schema['table']
        description = table_schema['description']
        anytable = AnyTable(table_name=table_name, description=description, table_schema = json.dumps(table_schema))
        db.session.add(anytable)
        db.session.commit()
        return "add table_schema"

@anytable_ns.route('/<int:id>')
class AnyTableResource(Resource):
    def get(self, id):
        return anytable_schema.jsonify(AnyTable.query.get(id))


    def put(self, id):
        return ""

    def delete(self, id):
        anytable = AnyTable.query.get(id)
        db.session.delete(anytable)
        db.session.commit()
        return "delete table"