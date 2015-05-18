__author__ = 'piotr'
from app import db
from sqlalchemy.exc import IntegrityError


class CatalogModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())


class Category(CatalogModel):
    __tablename__ = "categories"

    name = db.Column(db.String(128), unique=True, nullable=False)
    __all_items = db.relationship('Item', lazy='dynamic', backref="category", order_by="Item.name", cascade="delete")
    __latest_items = db.relationship('Item', lazy='dynamic', order_by='Item.date_created')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    def all_items(self):
        return self.__all_items.all()

    def number_of_items(self):
        return self.__all_items.count()

    def latest_items(self, limit=10):
        return self.latestItems[0:limit]

    def add_item(self, item):
        assert item is not None

        if not self.id:
            CatalogDAO.add_category(self)

        item.category_id = self.id
        db.session.add(item)


class Item(CatalogModel):
    __tablename__ = "items"

    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)

    def __init__(self, name, description=None):
        self.name = name
        self.description = description


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
        db.session.commit()

    @staticmethod
    def category_with_name(name):
        return Category.query.filter(Category.name == name).first()

    @staticmethod
    def category_with_id(category_id):
        return Category.query.filter(Category.id == category_id).first()

    @staticmethod
    def latest_categories():
        return []

    # Items methods
    @staticmethod
    def number_of_all_items():
        return Item.query.count()

    @staticmethod
    def latest_items(self):
        return []


