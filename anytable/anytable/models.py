import json
from flask import jsonify, request, current_app
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship, backref
from flask_restplus import Resource, Namespace
from inflector import Inflector
from anytable.extensions import api, ma, db
from anytable.base.models import Base

class AnyTable(Base):
    __tablename__ = 'anytables'

    table_name = Column(String, unique=True, nullable=True)
    description = Column(String, nullable=False)
    table_schema = Column(String, nullable=True)
    models = {}
    schemas = {}
    schemas_for_many = {}
    namespaces = {}
    resources = {}

    TYPE_DICT = {
        "integer": Integer,
        "float": Float,
        "string": String
    }

    def __repr__(self):
        return "<id={id} table_name={table_name} description={description} created_at={created_at} updated_at={updated_at}".format(id=self.id, table_name=self.table_name, description=self.description, created_at=self.created_at, updated_at=self.updated_at)

    def add_table(self):
        table_schema = json.loads(self.table_schema)
        self.models[self.table_name] = self._add_model(table_schema)
        self.schemas[self.table_name] = self._add_schema(self.models[self.table_name])
        self.schemas_for_many[self.table_name] = self._add_schema_for_many(self.models[self.table_name])
        self.namespaces[self.table_name] = self._add_namespace(self.table_name)
        self.resources[self.table_name] = self._add_resource(self.models[self.table_name], self.schemas_for_many[self.table_name], self.namespaces[self.table_name])
        api.add_namespace(self.namespaces[self.table_name])

    def _add_model(self, table_schema):
        return type(Inflector().classify(table_schema['table']), (Base, ), self._gen_dict(table_schema))

    def _gen_dict(self, table_schema):
        dic = {}
        dic['__tablename__'] = table_schema['table']
        dic['id'] = Column(Integer, primary_key=True, autoincrement=True)
        for field in table_schema['fields']:
            dic[field['name']] = Column(self.TYPE_DICT[field['type']], unique=field['unique'], nullable=field['nullable'])
        return dic

    def _add_schema(self, cls):
        class Schema(ma.ModelSchema):
            class Meta:
                model = cls
        return Schema()

    def _add_schema_for_many(self, cls):
        class Schema(ma.ModelSchema):
            class Meta:
                model = cls
        return Schema(many=True)

    def _add_namespace(self, ns):
        return Namespace(ns)

    def _add_resource(self, model, schema, ns):
            @ns.route('/')
            class MetaResources(Resource):
                def get(self):
                    return schema.jsonify(model.query.all())

                def post(self):
                    record_json = request.get_json()
                    record = model(**record_json)
                    db.session.add(record)
                    db.session.commit()
                    return "add record"

            @ns.route('/<int:id>')
            class MetaResource(Resource):
                def get(self, id):
                    return schema.jsonify(model.query.get(id))

                def delete(self, id):
                    record = model.query.get(id)
                    db.session.delete(record)
                    db.session.commit()
                    return "delete record"


