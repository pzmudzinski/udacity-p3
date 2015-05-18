from app import db

db.drop_all()
db.create_all()

# Add example entries
from app.mod_catalog.models import Category

sampleCategory1 = Category("Category 1")
sampleCategory2 = Category("Category 2")
sampleCategory3 = Category("Category 3")

db.session.add(sampleCategory1)
db.session.add(sampleCategory2)
db.session.add(sampleCategory3)

db.session.commit()