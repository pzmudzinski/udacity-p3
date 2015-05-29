# Import flask and template operators
from flask import Flask, redirect
from flask_marshmallow import Marshmallow
# Import SQLAlchemy
from flask.ext.sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.login import LoginManager

# Define the WSGI application object
app = Flask(__name__)

from app import views

# Configurations
app.config.from_object('config')

# Define the database object which is imported
# by modules and controllers
db = SQLAlchemy(app)
marshmallow = Marshmallow(app)
toolbar = DebugToolbarExtension(app)
login_manager = LoginManager()
login_manager.init_app(app)

from app.mod_catalog.views import blueprint_catalog as blueprint_catalog
from app.mod_catalog.views import blueprint_api as blueprint_api

app.register_blueprint(blueprint_catalog)
app.register_blueprint(blueprint_api)
# app.register_blueprint(xyz_module)
# ..

# Build the database:
# This will create the database file using SQLAlchemy
from app.mod_catalog.models import *

db.drop_all()
db.create_all()
import db_create
db_create.add_sample_categories()
