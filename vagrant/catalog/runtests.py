__author__ = 'piotr'
import os
import unittest
import time

from app import app, db, marshmallow
from app.mod_catalog.models import Category
from app.mod_catalog.models import Item
from app.mod_catalog.models import CatalogDAO
from flask import request
from flask import url_for
from flask import json

basedir = os.path.abspath(os.path.dirname(__file__))


class CatalogTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,
                                                                            'test.db')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class CatalogDAOTestCase(CatalogTestCase):
    def setUp(self):
        super(self.__class__, self).setUp()
        self.dao = CatalogDAO
        self.testCategory = Category("ABC")
        self.testItem = Item("ITEM", "DESC")

    def tearDown(self):
        super(self.__class__, self).tearDown()

    def testAddingCategory(self):
        self.assertEqual(self.dao.number_of_categories(), 0)
        self.dao.add_category(self.testCategory)
        self.assertEqual(self.dao.number_of_categories(), 1)
        assert self.testCategory.id is not None

    def testAddingCategoriesWithTheSameNames(self):
        self.dao.add_category(self.testCategory)
        category2 = Category("ABC")
        with self.assertRaises(ValueError):
            self.dao.add_category(category2)

    def testGettingCategoryWithName(self):
        self.dao.add_category(self.testCategory)
        self.dao.add_category(Category("ABC2"))
        self.assertEqual(self.testCategory, self.dao.category_with_name(self.testCategory.name),
                         'DAO didn\'t found category by name')

    def testDeletingCategory(self):
        self.dao.add_category(self.testCategory)
        self.dao.delete_category(self.testCategory)
        self.assertEqual(self.dao.number_of_categories(), 0)

    def testGettingAllCategories(self):
        for x in ['z', 'c', 'a', '0']:
            self.dao.add_category(Category(x))

        all_categories = self.dao.all_categories()
        self.assertEqual(all_categories[0].name, '0')
        self.assertEqual(all_categories[1].name, 'a')
        self.assertEqual(all_categories[3].name, 'z')

    def testAddingItem(self):
        self.dao.add_category(self.testCategory)
        self.assertEqual(self.testCategory.get_number_of_items(), 0)
        self.testCategory.add_item(self.testItem)
        self.assertEqual(self.testCategory.get_number_of_items(), 1)
        self.assertEqual(self.dao.number_of_all_items(), 1)
        self.assertIsNotNone(self.testItem.id)

    def testDeletingCategoryWithItems(self):
        self.dao.add_category(self.testCategory)

        self.testCategory.add_item(Item("abc1"))
        self.testCategory.add_item(Item("abc2"))
        self.testCategory.add_item(Item("abc3"))

        another_category = Category("another category")
        self.dao.add_category(another_category)

        another_category.add_item(Item("1"))

        self.assertEqual(self.dao.number_of_all_items(), 4)
        self.dao.delete_category(self.testCategory)
        self.assertEqual(self.dao.number_of_all_items(), 1)
        self.assertEqual(self.testCategory.get_number_of_items(), 0)

    def testAddingNoneItemRaisesException(self):
        with self.assertRaises(AssertionError):
            self.testCategory.add_item(None)

    def testGettingAllItems(self):
        self.dao.add_category(self.testCategory)
        self.testCategory.add_item(Item('z'))
        self.testCategory.add_item(Item('0'))
        self.testCategory.add_item(Item('b'))

        all_items = self.testCategory.get_all_items()
        self.assertEqual('0', all_items[0].name)
        self.assertEqual('z', all_items[2].name)

    def testAddingItemToCategoryWhichWasntAddedBefore(self):
        item = Item('a')
        self.testCategory.add_item(item)

        all_items = self.dao.number_of_all_items()

        self.assertEqual(1, all_items)
        self.assertIsNotNone(item.id)

    def testGettingLatestItems(self):
        i1 = Item('a')
        i2 = Item('b')
        i3 = Item('c')

        category1 = Category('c1')
        category2 = Category('c2')
        category3 = Category('c3')

        category1.add_item(i1)
        time.sleep(1)
        category2.add_item(i2)
        time.sleep(1)
        category3.add_item(i3)

        latest_items = self.dao.latest_items()
        self.assertEqual(i3, latest_items[0])
        self.assertEqual(i2, latest_items[1])
        self.assertEqual(i1, latest_items[2])

    def testGettingItemById(self):
        self.testCategory.add_item(self.testItem)
        self.assertEqual(self.testItem, self.dao.item_with_id(self.testItem.id))


class JSONEndpointsTestCase(CatalogTestCase):
    def setUp(self):
        super(self.__class__, self).setUp()
        self.dao = CatalogDAO
        self.testCategory = Category("ABC")
        self.testItem = Item("ITEM", "DESC")

    def tearDown(self):
        super(self.__class__, self).tearDown()

    def testGettingItemById(self):
        self.testCategory.add_item(self.testItem)

        with app.test_request_context():
            response = app.test_client().get(self.testItem.url)
            dict = json.loads(response.data)
            self.assertEqual(dict['category_id'], self.testCategory.id)
            self.assertEqual(dict['id'], self.testItem.id)

        self.assertIsNotNone(response.data)

    def testNotExistingItem(self):
        item = Item('a')
        item.id = 310
        with app.test_request_context():
            response = app.test_client().get(item.url)
            response_dict = json.loads(response.data)
            assert 'error' in response_dict

    def testGettingCategoryById(self):
        self.dao.add_category(self.testCategory)
        self.testCategory.add_item(self.testItem)

        with app.test_request_context():
            # print app.url_map
            response = app.test_client().get(self.testCategory.url)
            response_dict = json.loads(response.data)
            self.assertEqual(response_dict['id'], self.testCategory.id)

        self.assertIsNotNone(response.data)


if __name__ == '__main__':
    unittest.main()
