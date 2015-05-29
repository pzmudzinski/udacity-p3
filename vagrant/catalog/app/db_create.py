# Add example entries
from app.mod_catalog.models import *

def add_sample_categories():
    sampleCategory1 = Category("Category 1")
    sampleCategory2 = Category("Category 2")
    sampleCategory3 = Category("Category 3")

    CatalogDAO.add_category(sampleCategory1)
    CatalogDAO.add_category(sampleCategory2)
    CatalogDAO.add_category(sampleCategory3)
    add_sample_items()


def add_sample_items():
    category1 = CatalogDAO.category_with_name("Category 1")
    category1.add_item(Item("ABC"))
    category1.add_item(Item("LOL"))
