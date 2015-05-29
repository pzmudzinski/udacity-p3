__author__ = 'piotr'
from app import db
from sqlalchemy.exc import IntegrityError
from app import marshmallow
from flask import url_for
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import fields, Schema, ValidationError


class CatalogModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())


class Category(CatalogModel):
    __tablename__ = "categories"

    name = db.Column(db.String(128), unique=True, nullable=False)
    all_items = db.relationship('Item', lazy='dynamic', backref="category", order_by="Item.name", cascade="delete")
    latest_items = db.relationship('Item', lazy='dynamic', order_by='Item.date_created')

    def __init__(self, name):
        self.name = name

    def get_all_items(self):
        return self.all_items.all()

    def get_number_of_items(self):
        return self.all_items.count()

    def latest_items(self, limit=10):
        return self.latest_items[0:limit]

    def add_item(self, item):
        assert item is not None

        me_in_db = CatalogDAO.category_with_id(self.id)
        if me_in_db is None:
            db.session.add(self)
            self.all_items = [item]
            db.session.add(item)
        else:
            self.all_items.append(item)
            db.session.add(item)

        db.session.commit()

    @property
    def url(self):
        return url_for('api.get_category', category_id=self.id)

    def __repr__(self):
        return self.name


class Item(CatalogModel):
    __tablename__ = "items"

    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)

    def __init__(self, name, description=None):
        self.name = name
        self.description = description

    @property
    def url(self):
        return url_for('api.get_item', item_id=self.id)

    def __repr__(self):
        return self.name


def must_not_be_blank(data):
    if not data:
        raise ValidationError('Data not provided.')


class CategorySchema(marshmallow.Schema):
    items_count = fields.Function(lambda obj: obj.get_number_of_items())
    items = fields.Nested('ItemSchema', attribute='all_items', many=True, exclude=['category_id'])
    url = fields.Function(lambda category: category.url)
    name = fields.Str(required=True, validate=must_not_be_blank)

    class Meta:
        fields = ('id', 'name', 'items_count', 'items', 'url')
        # Smart hyperlinking


class ItemSchema(marshmallow.Schema):
    category = fields.Nested(CategorySchema, exclude=['items'])
    url = fields.Function(lambda category: category.url)
    category_id = fields.Int(validate=must_not_be_blank)

    class Meta:
        fields = ('id', 'name', 'description', 'category_id', 'url')


class CatalogDAO(object):
    # Categories methods
    @staticmethod
    def add_category(category):
        try:
            db.session.add(category)
            db.session.commit()
        except IntegrityError:
            raise ValueError('Category with the same name already exists.')

    @staticmethod
    def number_of_categories():
        return Category.query.count()

    @staticmethod
    def all_categories():
        return Category.query.order_by(Category.name).all()

    @staticmethod
    def delete_category(category):
        db.session.delete(category)
        return session_commit()

    @staticmethod
    def delete_category_with_id(category_id):
        db.session.delete(CatalogDAO.category_with_id(category_id))
        return session_commit()

    @staticmethod
    def delete_item(item_id):
        db.session.delete(CatalogDAO.item_with_id(item_id))
        return session_commit()

    @staticmethod
    def category_with_name(name):
        return Category.query.filter(Category.name == name).first()

    @staticmethod
    def category_with_id(category_id, throw404=False):
        q = Category.query.filter(Category.id == category_id)
        return q.first_or_404() if throw404 else q.first()

    @staticmethod
    def item_with_id(item_id, throw404=False):
        q = Item.query.filter(Item.id == item_id)
        return q.first_or_404() if throw404 else q.first()

    @staticmethod
    def latest_categories():
        q = Item.query.order_by(Item.date_created).limit(10)
        return q.all()

    # Items methods
    @staticmethod
    def number_of_all_items():
        return Item.query.count()

    @staticmethod
    def latest_items(limit=10):
        q = Item.query.order_by(Item.date_created.desc()).limit(limit)
        return q.all()


from datetime import datetime
import json


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)


def session_commit():
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        reason = str(e)
        return reason