from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Required

class AnyTableForm(FlaskForm):
    table_name = StringField('table name:', validators=[Required()])
    description = StringField('description:')
    table_schema = StringField('table schema:', validators=[Required()])
    submit = SubmitField('Add Table')
    reset = SubmitField('Reset')
