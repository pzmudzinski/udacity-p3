__author__ = 'piotr'

from flask.ext.wtf import Form
from wtforms import StringField, SelectField, IntegerField
from wtforms.validators import DataRequired
from .models import CatalogDAO


class AddItemForm(Form):
    name = StringField('name', validators=[DataRequired()])
    description = StringField('description')
    category = SelectField(u'category', coerce=int)

    def __init__(self):
        super(self.__class__, self).__init__()
        self.category.choices = [(g.id, g.name) for g in CatalogDAO.all_categories()]


class AddCategoryForm(Form):
    name = StringField('name', validators=[DataRequired()])


class DeleteItemForm(Form):
    id = IntegerField('id')
    name = StringField('name', validators=[DataRequired()])


class DeleteCategoryForm(Form):
    category = SelectField(u'category', coerce=int)

    def __init__(self):
        super(self.__class__, self).__init__()
        self.category.choices = [(g.id, g.name) for g in CatalogDAO.all_categories()]