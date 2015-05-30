from flask import Flask, redirect
from flask_marshmallow import Marshmallow
from flask.ext.sqlalchemy import SQLAlchemy
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
login_manager = LoginManager()
login_manager.init_app(app)

from app.mod_catalog.views import blueprint_catalog as blueprint_catalog
from app.mod_catalog.views import blueprint_api as blueprint_api

app.register_blueprint(blueprint_catalog)
app.register_blueprint(blueprint_api)

# Build the database:
# This will create the database file using SQLAlchemy
from app.mod_catalog.models import *

db.drop_all()
db.create_all()
import db_create

db_create.add_sample_categories()


@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('catalog.login'))