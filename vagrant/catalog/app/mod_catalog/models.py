__author__ = 'piotr'
from app import db
from app import marshmallow
from flask import url_for
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import fields, ValidationError
from flask.ext.login import UserMixin
from sqlalchemy.orm.exc import NoResultFound


class User(db.Model):
    __tablename__ = 'catalog_users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)

    def __init__(self, email, username):
        self.email = email
        self.username = username

    def __repr__(self):
        return "<User('%d', '%s', '%s')>" \
               % (self.id, self.username, self.email)

    @classmethod
    def get_or_create(cls, data):
        """
        data contains:
            {u'family_name': u'Surname',
            u'name': u'Name Surname',
            u'picture': u'https://link.to.photo',
            u'locale': u'en',
            u'gender': u'male',
            u'email': u'propper@email.com',
            u'birthday': u'0000-08-17',
            u'link': u'https://plus.google.com/id',
            u'given_name': u'Name',
            u'id': u'Google ID',
            u'verified_email': True}
        """
        try:
            # .one() ensures that there would be just one user with that email.
            # Although database should prevent that from happening -
            # lets make it buletproof
            user = db.session.query(cls).filter_by(email=data['email']).one()
        except NoResultFound:
            user = cls(
                email=data['email'],
                username=data['given_name'],
            )
            db.session.add(user)
            db.session.commit()
        return user

    def is_active(self):
        return True

    def is_authenticated(self):
        """
        Returns `True`. User is always authenticated. Herp Derp.
        """
        return True

    def is_anonymous(self):
        """
        Returns `False`. There are no Anonymous here.
        """
        return False

    def get_id(self):
        """
        Assuming that the user object has an `id` attribute, this will take
        that and convert it to `unicode`.
        """
        try:
            return unicode(self.id)
        except AttributeError:
            raise NotImplementedError("No `id` attribute - override get_id")

    def __eq__(self, other):
        """
        Checks the equality of two `UserMixin` objects using `get_id`.
        """
        if isinstance(other, UserMixin):
            return self.get_id() == other.get_id()
        return NotImplemented

    def __ne__(self, other):
        """
        Checks the inequality of two `UserMixin` objects using `get_id`.
        """
        equal = self.__eq__(other)
        if equal is NotImplemented:
            return NotImplemented
        return not equal


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


def session_commit():
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        reason = str(e)
        return reason