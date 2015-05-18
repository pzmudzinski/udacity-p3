__author__ = 'piotr'
import os
import unittest
import time

from app import app, db
from app.mod_catalog.models import Category
from app.mod_catalog.models import Item
from app.mod_catalog.models import CatalogDAO


class CatalogTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)),
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
        self.assertEqual(self.testCategory.number_of_items(), 0)
        self.testCategory.add_item(self.testItem)
        self.assertEqual(self.testCategory.number_of_items(), 1)
        self.assertEqual(self.dao.number_of_all_items(), 1)

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
        self.assertEqual(self.testCategory.number_of_items(), 0)

    def testAddingNoneItemRaisesException(self):
        with self.assertRaises(AssertionError):
            self.testCategory.add_item(None)

    def testGettingAllItems(self):
        self.dao.add_category(self.testCategory)
        self.testCategory.add_item(Item('z'))
        self.testCategory.add_item(Item('0'))
        self.testCategory.add_item(Item('b'))

        all_items = self.testCategory.all_items()
        self.assertEqual('0', all_items[0].name)
        self.assertEqual('z', all_items[2].name)

    def testAddingItemToCategoryWhichWasntAddedBefore(self):
        self.testCategory.add_item(Item('a'))

        all_items = self.dao.number_of_all_items()

        self.assertEqual(1, all_items)


if __name__ == '__main__':
    unittest.main()